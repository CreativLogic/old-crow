"""
mcp_servers/claude_acp_bridge.py

MCP server that bridges RAVEN's MCP protocol to claude-agent-acp (ACP).
Uses your existing Claude subscription — no API key needed.

RAVEN (MCP) → this bridge → claude-agent-acp (ACP) → Claude Agent SDK → Anthropic API
"""

import asyncio
import json
import os
import logging
import subprocess

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("claude-acp-bridge")

# The ACP subprocess
_acp_process = None


async def _get_acp():
    """Get or start the claude-agent-acp subprocess."""
    global _acp_process
    if _acp_process is None or _acp_process.poll() is not None:
        _acp_process = await asyncio.create_subprocess_exec(
            "claude-agent-acp",
            "--acp",
            "--stdio",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        logger.info("claude-agent-acp started")
    return _acp_process


async def _send_acp(message: dict) -> dict:
    """Send a JSON-RPC message to claude-agent-acp and return the response."""
    proc = await _get_acp()
    payload = json.dumps(message) + "\n"
    proc.stdin.write(payload.encode())
    await proc.stdin.drain()
    
    line = await asyncio.wait_for(proc.stdout.readline(), timeout=120)
    return json.loads(line.decode())


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="claude_chat",
            description="Send a message to Claude (via your subscription). Claude has access to files, shell, and web search.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message or task for Claude to process"
                    },
                    "model": {
                        "type": "string",
                        "description": "Claude model to use (default: claude-sonnet-4-5)",
                        "default": "claude-sonnet-4-5"
                    }
                },
                "required": ["message"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "claude_chat":
        message = arguments.get("message", "")
        model = arguments.get("model", "claude-sonnet-4-5")
        
        # Build ACP request
        acp_request = {
            "jsonrpc": "2.0",
            "method": "task",
            "params": {
                "prompt": message,
                "model": model,
            }
        }
        
        try:
            # We communicate via STDIO — for simplicity, use subprocess per-request
            proc = await asyncio.create_subprocess_exec(
                "claude-agent-acp",
                "--acp",
                "--stdio",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # ACP init
            init = json.dumps({"jsonrpc": "2.0", "method": "initialize", "params": {
                "protocolVersion": "0.1",
                "clientInfo": {"name": "raven", "version": "1.0"}
            }}) + "\n"
            proc.stdin.write(init.encode())
            await proc.stdin.drain()
            
            # Send the task
            task = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "task", "params": {
                "prompt": message
            }}) + "\n"
            proc.stdin.write(task.encode())
            await proc.stdin.drain()
            proc.stdin.close()
            
            # Read response
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
            
            if stdout:
                return [TextContent(type="text", text=stdout.decode(errors='replace')[:10000])]
            elif stderr:
                return [TextContent(type="text", text=f"[Claude ACP]: {stderr.decode(errors='replace')[:5000]}")]
            else:
                return [TextContent(type="text", text="[Claude ACP returned no output]")]
                
        except asyncio.TimeoutError:
            return [TextContent(type="text", text="[Claude ACP timed out after 300s]")]
        except Exception as e:
            return [TextContent(type="text", text=f"[Claude ACP error: {e}]")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
