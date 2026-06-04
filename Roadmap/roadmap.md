# RAVEN Roadmap
# Feature tracking, completed work, and future plans

---

## COMPLETED ✅

### Terminal Integration (June 3, 2026)
Built-in terminal panel accessible with Ctrl+` or rail button. Connects to a real shell via WebSocket. Uses GitHub dark theme with Roboto Mono font.
> Technical details: `Roadmap/raven_log.md#terminal-integration`

### Tool Stack (June 3, 2026)
Dashboard for managing all your tools, apps, and services. Comes with 25 pre-populated tools across AI APIs, Google Workspace, Web Apps, and Dev Tools. Add custom tools with credentials, notes, and usage tracking.
> Technical details: `Roadmap/raven_log.md#stack-tab`

### Visual Redesign (June 3, 2026)
Complete typography and color overhaul. Space Grotesk headers, Roboto body text, dark sidebar, purple gradient accents throughout. No more "sugarless cup of coffee" — the app has personality now.
> Technical details: `Roadmap/raven_log.md#visual-overhaul`

### Logo & Tagline (June 3, 2026)
Final branding: new logo image and tagline "Nested Intelligence, Orchestrated by Raven"

### Claude AI Access (June 3, 2026)
Claude Pro subscription bridged into RAVEN without needing a separate API key. Uses the ACP protocol to connect your existing subscription.
> Technical details: `Roadmap/raven_log.md#claude-acp-bridge`

### RAVEN Deployment (June 1-2, 2026)
RAVEN installed and running as a self-hosted AI operating system. Accessible on the local network. Custom branding applied.
> Technical details: `Roadmap/raven_log.md#2026-06-01-02`

### Apify Lead Generator (May 31, 2026)
Prospect list builder actor deployed for automated lead generation.

### Discord Bot (May 30, 2026)
BENTLEY#4163 connected to RAVEN's Discord server for notifications and commands.

---

## IN PROGRESS 🔧

### Service Health
- **ChromaDB**: DOWN — needs `pip install chromadb && chroma run --port 8100` + uncomment env vars
- **SearXNG**: DOWN — needs Docker or native install
- **Email**: Not configured — needs IMAP/SMTP env vars
- **Ntfy**: Not configured — needs push notification setup

### Missing Provider Keys
- OpenAI, Gemini, Groq, xAI, OpenRouter — all need API keys added to `.env`

### CSS Cleanup
style.css is 36,000 lines. Needs full audit and deduplication pass.

---

## PLANNED 📋

### Phase 2 — Intelligence Features
- **Dreams Tab**: Autonomous end-of-session agent sweep. Checks skills, session hygiene, cost intelligence, goal tracking, memory health. Auto-off toggle. Optional visual morning report card.
- **Mission Control**: Dashboard tab with 3 priority tasks and daily progress tracking through workflows.
- **API Usage Tracker**: Global dashboard tracking live usage, costs, and limits across all AI providers (DeepSeek, Claude, MiniMax, etc.)

### Phase 3 — Data & Memory
- **Memory Bulk Upload**: Add multiple files/folders at once for indexing. Show indexed file count.
- **Skills Folder Upload**: Support uploading entire skill folders (resources, eval subfolders).
- **Color-Coded Cards**: Gradient headers and highlight effects so different sections are visually distinct at a glance.

### Phase 4 — Integration & Power
- **Artifacts Section**: Rendered HTML/SVG/code outputs that persist beyond chat. Separate from Gallery.
- **File System Integration**: Folder picker, tree view, connect folders to Brain/File System tab.
- **Graphify Integration**: File indexing for faster, more accurate knowledge retrieval.
- **Obsidian + Pinecone + Notion**: Connect external knowledge bases to RAVEN memory.

### Phase 5 — Mobile & Distribution
- Mobile access for RAVEN (requires desktop app installed as hub, like Codex model)
- Multi-user access with separate workspaces

---

## IDEAS & BACKLOG 💡

- Agent prompt optimization for smaller local models (4k-16k context)
- Cookbook reliability across different machines/GPUs
- Better degraded-state reporting for services
- Email performance audit
- Provider setup/probing audit
- Self-host troubleshooting cookbook
- Accessibility pass (keyboard nav, focus states, contrast)
- First-run setup improvements
- Backup/restore guide
- Vendor CDN assets for fully offline mode


---

## TONIGHT — June 4, 2026 🔥

### Bugs
- **Theme color picker glitching**: Advanced color selection freezes, cards self-close
- **Theme coverage gaps**: Some areas don't apply theme colors. Need SVG transparent logo variant
- **Missing theme controls**: Button bg/text, section-specific text colors, scrollbar color
- **Card text too small**: All cards need bump to ~16px (matching chat input size)
- **Username too small**: Sidebar logged-in username needs size increase
- **Layout glitches**: Cards closing themselves, sections not snapping, modal positioning fragile
- **Notes editor**: Missing bold/italic/bullets/links/text size and markdown mode

### Onboarding
- Welcome screen: ask preferred name, hourly rate slider ($0-$5k), calculate savings
- Savings calculator: tasks_completed × time_saved × hourly_rate → dashboard display

### Home Dashboard
- New sidebar tab with live cards: token usage, 3 priority tasks, weekly goal progress bar, tasks completed, reminders, top 5 workflows, Pomodoro timer (global ticker)

### Quick UI Fixes
- Add scrollbar color to theme advanced options
- Add button bg/text color to theme advanced options  
- Add section-specific text color targeting
- Bump all card text to 16px universally
- Sidebar username font size increase

> Detailed checklist: `Roadmap/TONIGHT.md`
