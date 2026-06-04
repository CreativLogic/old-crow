/**
 * Terminal Module — xterm.js WebSocket PTY integration.
 * Toggleable terminal panel at the bottom of the chat view.
 */

let _term = null;
let _fitAddon = null;
let _ws = null;
let _open = false;
let _panel = null;
let _resizeObserver = null;

function _ensurePanel() {
  if (_panel) return _panel;

  _panel = document.createElement('div');
  _panel.id = 'terminal-panel';
  _panel.className = 'terminal-panel';
  _panel.innerHTML = `
    <div class="terminal-header">
      <span class="terminal-title">Terminal</span>
      <div class="terminal-header-actions">
        <button class="terminal-header-btn" id="terminal-min-btn" title="Minimize">_</button>
        <button class="terminal-header-btn" id="terminal-max-btn" title="Maximize">[]</button>
        <button class="terminal-header-btn" id="terminal-close-btn" title="Close">x</button>
      </div>
    </div>
    <div class="terminal-body" id="terminal-body"></div>
  `;

  document.body.appendChild(_panel);
  return _panel;
}

async function _connect() {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${proto}//${window.location.host}/api/terminal/ws`;

  _ws = new WebSocket(wsUrl);
  _ws.binaryType = 'arraybuffer';

  _ws.onopen = () => {
    console.log('[Terminal] Connected');
    _term.clear();
    _term.focus();
  };

  _ws.onmessage = (event) => {
    if (event.data instanceof ArrayBuffer) {
      const uint8 = new Uint8Array(event.data);
      _term.write(uint8);
    } else if (typeof event.data === 'string') {
      _term.write(event.data);
    }
  };

  _ws.onclose = () => {
    console.log('[Terminal] Disconnected');
    _term.write('\r\n\x1b[31m[disconnected]\x1b[0m\r\n');
  };

  _ws.onerror = (err) => {
    console.error('[Terminal] WebSocket error', err);
  };

  // Wait for connection
  return new Promise((resolve) => {
    _ws.onopen = () => {
      console.log('[Terminal] Connected');
      _term.clear();
      _term.focus();
      resolve();
    };
  });
}

function _sendResize() {
  if (!_ws || _ws.readyState !== WebSocket.OPEN) return;
  const dims = _fitAddon.proposeDimensions();
  if (!dims) return;
  _ws.send(JSON.stringify({ cols: dims.cols, rows: dims.rows }));
}

async function openTerminal() {
  if (_open) return;

  const panel = _ensurePanel();
  panel.style.display = 'flex';

  // Init xterm if not yet created
  if (!_term) {
    const terminalBody = document.getElementById('terminal-body');
    _term = new Terminal({
      cursorBlink: true,
      cursorStyle: 'bar',
      fontSize: 13,
      fontFamily: "'Roboto Mono', 'JetBrains Mono', 'Fira Code', monospace",
      theme: {
        background: '#0d1117',
        foreground: '#c9d1d9',
        cursor: '#58a6ff',
        selectionBackground: '#264f78',
        black: '#484f58',
        red: '#ff7b72',
        green: '#3fb950',
        yellow: '#d29922',
        blue: '#58a6ff',
        magenta: '#bc8cff',
        cyan: '#39c5d3',
        white: '#b1bac4',
        brightBlack: '#6e7681',
        brightRed: '#ffa198',
        brightGreen: '#56d364',
        brightYellow: '#e3b341',
        brightBlue: '#79c0ff',
        brightMagenta: '#d2a8ff',
        brightCyan: '#56d4dd',
        brightWhite: '#f0f6fc',
      },
      allowProposedApi: true,
    });

    _fitAddon = new FitAddon.FitAddon();
    _term.loadAddon(_fitAddon);
    _term.loadAddon(new WebLinksAddon.WebLinksAddon());

    _term.open(terminalBody);
    _fitAddon.fit();

    // Resize observer
    _resizeObserver = new ResizeObserver(() => {
      _fitAddon.fit();
      _sendResize();
    });
    _resizeObserver.observe(terminalBody);

    // Send resize on terminal resize
    _term.onResize(() => {
      _sendResize();
    });

    // Send input to backend
    _term.onData((data) => {
      if (_ws && _ws.readyState === WebSocket.OPEN) {
        _ws.send(data);
      }
    });
  }

  // Connect WebSocket
  if (!_ws || _ws.readyState !== WebSocket.OPEN) {
    await _connect();
  }

  panel.classList.add('terminal-open');
  _open = true;

  // Adjust chat container
  const chatContainer = document.getElementById('chat-container');
  if (chatContainer) {
    chatContainer.style.paddingBottom = '300px';
  }

  // Focus terminal
  setTimeout(() => {
    _fitAddon.fit();
    _sendResize();
    _term.focus();
  }, 100);
}

function closeTerminal() {
  if (!_open) return;

  if (_ws) {
    _ws.close();
    _ws = null;
  }

  _open = false;
  if (_panel) {
    _panel.classList.remove('terminal-open');
    _panel.style.display = 'none';
  }

  const chatContainer = document.getElementById('chat-container');
  if (chatContainer) {
    chatContainer.style.paddingBottom = '';
  }
}

function toggleTerminal() {
  if (_open) {
    closeTerminal();
  } else {
    openTerminal();
  }
}

function isTerminalOpen() {
  return _open;
}

// Keybinding: Ctrl+` to toggle terminal
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === '`') {
    e.preventDefault();
    toggleTerminal();
  }
});

// Wire rail button
document.addEventListener('DOMContentLoaded', () => {
  const railBtn = document.getElementById('rail-terminal');
  if (railBtn) {
    railBtn.addEventListener('click', () => {
      toggleTerminal();
      railBtn.classList.toggle('active-section', _open);
    });
  }
});

export default {
  open: openTerminal,
  close: closeTerminal,
  toggle: toggleTerminal,
  isOpen: isTerminalOpen,
};
