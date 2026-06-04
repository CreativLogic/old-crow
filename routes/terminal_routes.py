"""
Terminal routes — WebSocket PTY backend for xterm.js integration.

Spawns a real shell process via pty and bridges stdin/stdout over a WebSocket.
Supports resize events (SIGWINCH) so the PTY matches the xterm.js viewport.
"""

import asyncio
import logging
import os
import pty
import struct
import termios
import fcntl
import signal

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


def _set_pty_size(fd: int, rows: int, cols: int) -> None:
    """Set the PTY window size via TIOCSWINSZ."""
    try:
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
    except Exception:
        pass


async def _read_pty(fd: int, ws: WebSocket) -> None:
    """Read from PTY and send to WebSocket."""
    loop = asyncio.get_event_loop()
    while True:
        try:
            data = await loop.run_in_executor(None, os.read, fd, 4096)
            if not data:
                break
            await ws.send_bytes(data)
        except (OSError, asyncio.CancelledError):
            break
        except Exception:
            break


async def terminal_ws(websocket: WebSocket) -> None:
    """WebSocket endpoint for terminal PTY bridge."""
    await websocket.accept()
    logger.info("Terminal WebSocket connected")

    pid = None
    fd = None

    try:
        # Spawn a shell via PTY
        shell_cmd = os.environ.get("SHELL", "/bin/bash")
        pid, fd = pty.fork()

        if pid == 0:
            # Child process — launch shell in RAVEN's home directory
            os.environ.setdefault("TERM", "xterm-256color")
            os.environ.setdefault("COLORTERM", "truecolor")
            os.environ.setdefault("HOME", os.path.expanduser("~"))
            os.environ.setdefault("RAVEN_URL", "http://localhost:7000")
            # Add raven CLI to PATH
            path = os.environ.get("PATH", "")
            local_bin = os.path.expanduser("~/.local/bin")
            if local_bin not in path:
                os.environ["PATH"] = f"{local_bin}:{path}"
            # Start in RAVEN project directory
            raven_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.chdir(raven_dir)
            os.execve(shell_cmd, [shell_cmd], os.environ)
            os._exit(1)

        # Parent — bridge PTY to WebSocket
        # Set default terminal size
        _set_pty_size(fd, 24, 80)

        # Start reading from PTY
        read_task = asyncio.create_task(_read_pty(fd, websocket))

        # Listen for input from browser
        while True:
            try:
                msg = await websocket.receive()
            except WebSocketDisconnect:
                break

            if msg["type"] == "websocket.receive":
                if "text" in msg:
                    text = msg["text"]
                    # Handle resize JSON messages
                    if text.startswith('{"cols":'):
                        try:
                            import json
                            resize = json.loads(text)
                            cols = resize.get("cols", 80)
                            rows = resize.get("rows", 24)
                            _set_pty_size(fd, rows, cols)
                            # Send SIGWINCH to child process
                            os.kill(pid, signal.SIGWINCH)
                        except Exception:
                            pass
                    else:
                        # Raw text input
                        os.write(fd, text.encode())
                elif "bytes" in msg:
                    os.write(fd, msg["bytes"])

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Terminal error: {e}")
    finally:
        # Cleanup
        if read_task:
            read_task.cancel()
            try:
                await read_task
            except (asyncio.CancelledError, Exception):
                pass
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                try:
                    os.waitpid(pid, os.WNOHANG)
                except Exception:
                    pass
            except Exception:
                pass
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass

    logger.info("Terminal WebSocket disconnected")


def setup_terminal_routes() -> APIRouter:
    """Create and return the terminal router."""
    router = APIRouter(prefix="/api/terminal", tags=["terminal"])
    router.add_websocket_route("/ws", terminal_ws)
    return router
