# RAVEN Technical Changelog
# Updated: 2026-06-04 00:05 ET

---

## 2026-06-03 (Late Session) — Feature Build + Visual Overhaul

### Terminal Integration
- **routes/terminal_routes.py**: WebSocket PTY backend using Python `pty` module + `asyncio`
- SIGWINCH resize support, signal handling (SIGTERM cleanup)
- Registered at `/api/terminal/ws` with timeout exemption
- **static/lib/xterm/**: xterm.js v5.5.0, addon-fit v0.10.0, addon-web-links v0.11.0
- **static/js/terminal.js**: Frontend module with GitHub dark theme, Ctrl+` toggle
- **static/style.css**: Terminal panel CSS (`.terminal-panel`, `.terminal-header`, etc.)
- **static/index.html**: Rail button (terminal icon), xterm.js CSS/JS loaded
- **app.py**: Route registered + timeout exempt

### Stack Tab (Tool Management)
- **routes/stack_routes.py**: Full CRUD API at `/api/stack/tools`
- SQLite `stack_tools` table auto-created with 25 pre-seeded tools
- 4 categories: AI APIs (7), Google Workspace (6), Web Apps (6), Dev Tools (4)
- **static/js/stack.js**: Grid view, category filters, add/edit/delete forms
- **static/style.css**: Stack card CSS, category pills, form styles
- **static/index.html**: Rail button (server-rack icon), stack.js loaded

### Visual Overhaul
- **Fonts**: Space Grotesk (headers), Roboto (body), Roboto Mono (terminal/code)
- **Sidebar**: Background `#08080d` (black), 12px section titles, 13px list items
- **Sidebar brand**: Logo + gradient purple name
- **Purple gradient accent**: `#8b5cf6 → #6366f1` — cards, buttons, tabs, modals
- **Icon rail**: Buttons 40x40px (was 34x34), SVGs 20x20 (was 16x16), neon drop-shadow glow
- **Cards**: Purple left-border on hover, gradient skill headers
- **Send button**: Purple gradient + glow shadow
- **Section icons**: Purple tint + drop-shadow
- **Tab sizes**: Cookbook 13px/8px, Memory 13px/10px

### Logo & Tagline
- Logo: `RAVEN_AIOS_FINAL_LOGO.jpg` → copied to `static/`
- Updated in: index.html, landing.html, login.html, docs/index.html, manifest.json, theme.js
- Tagline: "Nested Intelligence, Orchestrated by Raven" (was "Give your soul wings")
- MIME types fixed: `image/png` → `image/jpeg`

### Claude ACP Bridge Fix
- **mcp_servers/claude_acp_bridge.py**: Added missing `--acp --stdio` flags to subprocess spawns
- Bridge was spawning `claude-agent-acp` without ACP mode flags — Claude access was broken

### Git
- Commit `eb00178`: 18 files, +2192/-77
- Pushed to `github.com/CreativLogic/RAVEN`

---

## 2026-06-03 (Early Session) — Claude Bridge + RAVEN Deploy

### Claude ACP Bridge
- Installed `@agentclientprotocol/claude-agent-acp@0.40.0` globally (npm)
- Created `mcp_servers/claude_acp_bridge.py` (MCP-to-ACP proxy, 144 lines)
- Registered as "Built-in: Claude (via subscription)" in `builtin_mcp.py`
- Exposes `claude_chat` tool to RAVEN agent
- Architecture: RAVEN (MCP) → bridge → claude-agent-acp (ACP) → Claude Agent SDK → Anthropic API
- Uses existing Claude Pro subscription — no API key needed

### RAVEN Deploy
- 6 commits pushed to `CreativLogic/RAVEN`
- Custom PNG logo, navy+cyan palette
- 4 API keys in `.env` (DeepSeek, MiniMax v1/v2)
- Running at `http://192.168.12.180:7000` (native, no Docker)

### Discoveries
- Claude OAuth tokens (`sk-ant` format in `~/.claude/.credentials.json`) are scoped to Claude Code internal API only
- Cannot use Claude subscription tokens as direct API keys
- ACP bridge is the workaround for subscription-based Claude access

---

## 2026-06-01-02 — RAVEN Rebranding
- 190 files changed across 6 commits
- Custom PNG logo, navy+cyan palette
- 4 API keys in `.env`

---

## 2026-05-31 — Apify Actor
- `prospect-list-builder` actor deployed live
- URL: `https://console.apify.com/actors/mbLhNz2COpeNk98Dj`
- Account: socialpatter

---

## 2026-05-30 — Discord Mission Control
- BENTLEY#4163 bot operational
- Server: "The Board Room" (1509815401507323944)
- Home channel: #conference-room (1509834931390517449)

---

## 2026-05-29 — Agent Team
- 41 skills installed
- 5-agent team scaffolded (Brandy, Dev, Leo, Draper, Mark)
- Workspace: `/home/vinfamous/AIOS/Social-Patter` established

---

## 2026-06-04 — CLI Bridge + IDE Terminal

### raven CLI Command
- **raven-cli**: Python CLI that sends natural language to RAVEN's agent from any terminal
- Installed to `~/.local/bin/raven`, added to PATH in `.bashrc`
- Streams NDJSON responses from `/api/cli/chat` endpoint
- Usage: `raven "fix the CSS"` or `raven --model deepseek "explain code"`

### CLI Agent Endpoint
- **routes/cli_routes.py**: Dedicated `/api/cli/chat` POST endpoint
- Uses persistent CLI session (`cli-terminal`) so context builds across calls
- Auto-selects first available model endpoint if none configured
- Returns NDJSON streaming response

### Terminal Integration Improvements
- Terminal now spawns in RAVEN project directory (`os.chdir(raven_dir)`)
- Sets `RAVEN_URL=http://localhost:7000` in terminal env
- Adds `~/.local/bin` to PATH so `raven` command is available
- Agent already has `bash` tool — can run shell commands with full filesystem access

### Claude ACP Bridge Fix
- Added missing `--acp --stdio` flags to subprocess spawns
- Was spawning `claude-agent-acp` without ACP mode — Claude access was broken


---

## 2026-06-04 (Planned — Overnight) — Bugs, Home Dashboard, Onboarding

### Bug Fixes Planned
- Theme color picker glitching in advanced section
- Theme coverage gaps (need SVG transparent logo variant)
- Missing theme controls: button bg/text, section text colors, scrollbar
- Card text bump to 16px universally
- Sidebar username font size increase
- Cards closing themselves + sections not snapping
- Notes editor: bold/italic/bullets/links/text size control + markdown mode

### Features Planned
- **Home Dashboard**: New sidebar tab with token usage, priority tasks, weekly goal progress, reminders, workflows, Pomodoro timer
- **Onboarding**: Welcome screen (name + hourly rate calculator)
- **File System**: File access + markdown editor with file tree
