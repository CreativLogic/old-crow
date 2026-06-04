/**
 * Stack Module — Tool & app stack management.
 * Pre-populated with common tools, custom add/edit/delete.
 */

const API = '/api/stack';

let _open = false;
let _modal = null;
let _tools = [];
let _activeCategory = null;

const CATEGORY_ICONS = {
  'ai-api': '🧠',
  'google-workspace': '📧',
  'web-app': '🌐',
  'dev-tool': '🔧',
  'other': '📦',
};

const CATEGORY_LABELS = {
  'ai-api': 'AI APIs',
  'google-workspace': 'Google Workspace',
  'web-app': 'Web Apps',
  'dev-tool': 'Dev Tools',
  'other': 'Other',
};

async function _fetchTools() {
  try {
    const url = _activeCategory ? `${API}/tools?category=${encodeURIComponent(_activeCategory)}` : `${API}/tools`;
    const res = await fetch(url);
    const data = await res.json();
    _tools = data.tools || [];
    _renderGrid();
  } catch (e) {
    console.error('[Stack] Fetch error:', e);
  }
}

function _renderGrid() {
  const grid = document.getElementById('stack-grid');
  if (!grid) return;

  if (_tools.length === 0) {
    grid.innerHTML = '<div class="stack-empty">No tools in this category. <button class="stack-add-first" id="stack-add-first-btn">+ Add your first tool</button></div>';
    setTimeout(() => {
      const btn = document.getElementById('stack-add-first-btn');
      if (btn) btn.onclick = _showAddForm;
    }, 50);
    return;
  }

  grid.innerHTML = _tools.map(t => `
    <div class="stack-card" data-id="${t.id}">
      <div class="stack-card-icon">${t.icon || '🔧'}</div>
      <div class="stack-card-body">
        <div class="stack-card-name">${_escape(t.name)}</div>
        <div class="stack-card-cat">${CATEGORY_LABELS[t.category] || t.category}</div>
        ${t.url ? `<a class="stack-card-url" href="${_escape(t.url)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${_escape(t.url)}</a>` : ''}
        ${t.notes ? `<div class="stack-card-notes">${_escape(t.notes)}</div>` : ''}
        ${t.api_key_masked ? `<div class="stack-card-key">🔑 ${_escape(t.api_key_masked)}</div>` : ''}
        ${t.usage_limit ? `<div class="stack-card-limit">📊 ${_escape(t.usage_limit)}</div>` : ''}
      </div>
      <div class="stack-card-actions">
        <button class="stack-card-btn" title="Edit" data-action="edit" data-id="${t.id}">✏️</button>
        <button class="stack-card-btn" title="Delete" data-action="delete" data-id="${t.id}">🗑️</button>
      </div>
    </div>
  `).join('');

  // Wire card buttons
  grid.querySelectorAll('[data-action="edit"]').forEach(btn => {
    btn.onclick = (e) => {
      e.stopPropagation();
      const id = parseInt(btn.dataset.id);
      const tool = _tools.find(t => t.id === id);
      if (tool) _showEditForm(tool);
    };
  });
  grid.querySelectorAll('[data-action="delete"]').forEach(btn => {
    btn.onclick = async (e) => {
      e.stopPropagation();
      const id = parseInt(btn.dataset.id);
      if (confirm('Remove this tool from your stack?')) {
        await fetch(`${API}/tools/${id}`, { method: 'DELETE' });
        _fetchTools();
      }
    };
  });
}

function _escape(s) {
  if (!s) return '';
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function _renderCategories() {
  fetch(`${API}/categories`).then(r => r.json()).then(cats => {
    const el = document.getElementById('stack-categories');
    if (!el) return;
    const allActive = !_activeCategory ? ' active' : '';
    let html = `<button class="stack-cat-btn${allActive}" data-cat="">All</button>`;
    cats.forEach(c => {
      const active = _activeCategory === c.category ? ' active' : '';
      html += `<button class="stack-cat-btn${active}" data-cat="${_escape(c.category)}">${CATEGORY_ICONS[c.category] || ''} ${CATEGORY_LABELS[c.category] || c.category} <span class="stack-cat-count">${c.count}</span></button>`;
    });
    el.innerHTML = html;
    el.querySelectorAll('.stack-cat-btn').forEach(btn => {
      btn.onclick = () => {
        _activeCategory = btn.dataset.cat || null;
        _renderCategories();
        _fetchTools();
      };
    });
  });
}

function _showAddForm(prefill = {}) {
  const form = document.getElementById('stack-form');
  if (!form) return;
  form.style.display = 'block';
  document.getElementById('stack-form-title').textContent = prefill.id ? 'Edit Tool' : 'Add Tool';
  document.getElementById('stack-name').value = prefill.name || '';
  document.getElementById('stack-category').value = prefill.category || 'other';
  document.getElementById('stack-url').value = prefill.url || '';
  document.getElementById('stack-icon').value = prefill.icon || '';
  document.getElementById('stack-notes').value = prefill.notes || '';
  document.getElementById('stack-api-key').value = prefill.api_key_masked || '';
  document.getElementById('stack-usage-limit').value = prefill.usage_limit || '';
  document.getElementById('stack-cost').value = prefill.cost_per_unit || '';
  form.dataset.editId = prefill.id || '';
  document.getElementById('stack-save-btn').textContent = prefill.id ? 'Update' : 'Add Tool';
}

function _showEditForm(tool) {
  _showAddForm(tool);
}

async function _saveTool() {
  const form = document.getElementById('stack-form');
  const editId = form.dataset.editId;

  const data = {
    name: document.getElementById('stack-name').value.trim(),
    category: document.getElementById('stack-category').value,
    url: document.getElementById('stack-url').value.trim() || null,
    icon: document.getElementById('stack-icon').value.trim() || null,
    notes: document.getElementById('stack-notes').value.trim() || null,
    api_key_masked: document.getElementById('stack-api-key').value.trim() || null,
    usage_limit: document.getElementById('stack-usage-limit').value.trim() || null,
    cost_per_unit: document.getElementById('stack-cost').value.trim() || null,
    tags: [],
  };

  if (!data.name) return alert('Tool name is required');

  try {
    const url = editId ? `${API}/tools/${editId}` : `${API}/tools`;
    const method = editId ? 'PUT' : 'POST';
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (res.ok) {
      form.style.display = 'none';
      form.dataset.editId = '';
      _fetchTools();
      _renderCategories();
    } else {
      alert('Failed to save tool');
    }
  } catch (e) {
    console.error('[Stack] Save error:', e);
  }
}

function _ensureModal() {
  if (_modal) return _modal;

  _modal = document.createElement('div');
  _modal.id = 'stack-modal';
  _modal.className = 'modal-overlay';
  _modal.innerHTML = `
    <div class="modal-panel stack-panel">
      <div class="modal-header">
        <h2>🔧 Tool Stack</h2>
        <button class="modal-close-btn" id="stack-close-btn">✕</button>
      </div>
      <div class="stack-categories" id="stack-categories"></div>
      <div class="stack-toolbar">
        <button class="stack-add-btn" id="stack-add-btn">+ Add Tool</button>
      </div>
      <div class="stack-grid" id="stack-grid"></div>
      <div class="stack-form" id="stack-form" style="display:none">
        <h3 id="stack-form-title">Add Tool</h3>
        <div class="stack-form-row">
          <input id="stack-name" placeholder="Tool name *" class="stack-input" />
          <select id="stack-category" class="stack-input">
            <option value="ai-api">AI API</option>
            <option value="google-workspace">Google Workspace</option>
            <option value="web-app">Web App</option>
            <option value="dev-tool">Dev Tool</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div class="stack-form-row">
          <input id="stack-url" placeholder="URL (optional)" class="stack-input" />
          <input id="stack-icon" placeholder="Icon emoji (optional)" class="stack-input" style="max-width:120px" />
        </div>
        <textarea id="stack-notes" placeholder="Notes..." class="stack-textarea" rows="2"></textarea>
        <div class="stack-form-row">
          <input id="stack-api-key" placeholder="API Key (masked)" class="stack-input" />
          <input id="stack-usage-limit" placeholder="Usage limit" class="stack-input" />
          <input id="stack-cost" placeholder="Cost/unit" class="stack-input" style="max-width:120px" />
        </div>
        <div class="stack-form-actions">
          <button id="stack-save-btn" class="stack-save-btn">Add Tool</button>
          <button id="stack-cancel-btn" class="stack-cancel-btn">Cancel</button>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(_modal);

  // Wire events
  document.getElementById('stack-close-btn').onclick = closeStack;
  document.getElementById('stack-add-btn').onclick = () => _showAddForm();
  document.getElementById('stack-save-btn').onclick = _saveTool;
  document.getElementById('stack-cancel-btn').onclick = () => {
    document.getElementById('stack-form').style.display = 'none';
  };
  _modal.onclick = (e) => { if (e.target === _modal) closeStack(); };

  return _modal;
}

function openStack() {
  if (_open) return;
  _ensureModal();
  _modal.style.display = 'flex';
  _open = true;
  _fetchTools();
  _renderCategories();
  const railBtn = document.getElementById('rail-stack');
  if (railBtn) railBtn.classList.add('active-section');
}

function closeStack() {
  if (!_open) return;
  _modal.style.display = 'none';
  _open = false;
  const railBtn = document.getElementById('rail-stack');
  if (railBtn) railBtn.classList.remove('active-section');
}

function toggleStack() {
  if (_open) closeStack();
  else openStack();
}

// Wire rail button
document.addEventListener('DOMContentLoaded', () => {
  const railBtn = document.getElementById('rail-stack');
  if (railBtn) {
    railBtn.addEventListener('click', toggleStack);
  }
});

export default { open: openStack, close: closeStack, toggle: toggleStack };
