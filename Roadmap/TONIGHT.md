# TONIGHT — June 4, 2026
# Priority task list (ordered by impact)

---

## BUGS — Fix First

### Theme System
- [ ] **Color picker bug**: Advanced color selection area under Themes is glitching — sections freeze, cards close themselves
- [ ] **Theme coverage gaps**: Built-in theme editor doesn't apply to all areas. SVG logo with transparent background needed for theme compatibility (keep browser favicon as-is)
- [ ] **Missing color controls**: Button background + text color not separately customizable in advanced section
- [ ] **Missing color controls**: Text colors in different sections need specific targeting (cards, sidebar, chat, modals — matching is too difficult without granular controls)
- [ ] **Missing color control**: Page scrollbar/slider color not customizable

### UI Sizing
- [ ] **Logged-in username too small** on sidebar
- [ ] **Card text too small everywhere** — bump to 16px (match chat input size). Affects: memory cards, skill cards, doclib cards, note cards, cookbook cards, stack cards

### Layout Glitches
- [ ] Cards closing by themselves
- [ ] Sections freezing or not snapping to proper areas when moved
- [ ] Modal/window positioning fragile (noted in earlier session)

---

## FEATURES

### Home Dashboard Tab (Sidebar)
New "Home" rail button that opens a live dashboard with cards:
- [ ] Token usage (live counter across all providers)
- [ ] Priority tasks (top 3, editable)
- [ ] Progress bar toward main weekly goal (interactive)
- [ ] Tasks completed today
- [ ] Reminders visible (next 3)
- [ ] Bundled workflows (top 5 most-used)
- [ ] Pomodoro timer (set time, global ticker visible in any tab)
- [ ] **Free drag & drop**: Cards freely movable by dragging anywhere on screen
- [ ] **6 cards per window**: Allow up to 6 cards visible in a single dashboard view

### Onboarding Flow
- [ ] Welcome screen: asks for user's preferred name
- [ ] Splash screen 2: "What is your time worth per hour?" slider ($0-$5,000)
- [ ] Calculator: money saved = tasks_completed × time_saved × hourly_rate → visible on home dashboard

### Notes Editor
- [ ] Text size adjustment
- [ ] Bold, italic, bullet formatting
- [ ] Link insertion
- [ ] Markdown editor mode

### File System
- [ ] File access integration
- [ ] Markdown editor with file tree

---

## QUICK WINS (do while sleeping)

- [ ] SVG logo with transparent background for theme editor
- [ ] Bump all card text to 16px
- [ ] Sidebar username font size increase
- [ ] Add scrollbar color to theme advanced options
- [ ] Add button bg/text color to theme advanced options
- [ ] Add section-specific text color controls to theme editor
