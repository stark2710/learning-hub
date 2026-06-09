/**
 * Global AI Settings widget — included on every page.
 * Manages: ai_provider, claude_api_key, ollama_model in localStorage.
 * Fires CustomEvent 'aisettings:changed' on save so pages can react.
 */
(function () {
  // ── Styles ──────────────────────────────────────────────────────────────
  const css = `
    #ais-fab {
      position: fixed;
      bottom: 22px;
      right: 22px;
      z-index: 8800;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #1e2130;
      border: 1px solid #2d3148;
      color: #94a3b8;
      font-size: 17px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 20px rgba(0,0,0,0.4);
      transition: all 0.2s;
    }
    #ais-fab:hover { color: #fff; border-color: #7c3aed; box-shadow: 0 4px 24px rgba(124,58,237,0.5); }
    #ais-fab.prov-ollama       { border-color: #059669; box-shadow: 0 4px 20px rgba(5,150,105,0.35); }
    #ais-fab.prov-claude      { border-color: #7c3aed; box-shadow: 0 4px 20px rgba(124,58,237,0.35); }
    #ais-fab.prov-local-claude{ border-color: #0891b2; box-shadow: 0 4px 20px rgba(8,145,178,0.35); }

    #ais-overlay {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 8900;
      background: rgba(0,0,0,0.55);
      backdrop-filter: blur(3px);
    }
    #ais-overlay.open { display: block; }

    #ais-modal {
      display: none;
      position: fixed;
      bottom: 74px;
      right: 22px;
      z-index: 8901;
      background: #1a1d27;
      border: 1px solid #2d3148;
      border-radius: 16px;
      padding: 22px 22px 18px;
      width: 320px;
      max-width: calc(100vw - 44px);
      box-shadow: 0 20px 60px rgba(0,0,0,0.7);
      animation: aisSlideUp 0.2s ease;
    }
    #ais-modal.open { display: block; }

    @keyframes aisSlideUp {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .ais-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
    .ais-title { font-size: 14px; font-weight: 700; color: #e2e8f0; }
    .ais-close-btn {
      background: none; border: none; color: #64748b; font-size: 18px;
      cursor: pointer; line-height: 1; padding: 0;
    }
    .ais-close-btn:hover { color: #e2e8f0; }
    .ais-sub { font-size: 11px; color: #64748b; margin-bottom: 16px; }

    .ais-toggle {
      display: flex;
      background: #0d1117;
      border: 1px solid #2d3148;
      border-radius: 8px;
      padding: 3px;
      gap: 3px;
      margin-bottom: 14px;
    }
    .ais-tog-btn {
      flex: 1;
      padding: 5px 10px;
      border: none;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s;
    }
    .ais-tog-btn.on-claude       { background: #7c3aed; color: #fff; }
    .ais-tog-btn.on-ollama       { background: #059669; color: #fff; }
    .ais-tog-btn.on-local-claude { background: #0891b2; color: #fff; }
    .ais-tog-btn.off             { background: none; color: #64748b; }

    .ais-label { font-size: 11px; color: #94a3b8; margin-bottom: 5px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
    .ais-input, .ais-select {
      width: 100%;
      background: #0d1117;
      border: 1px solid #2d3148;
      border-radius: 8px;
      color: #e2e8f0;
      padding: 8px 11px;
      font-size: 13px;
      box-sizing: border-box;
      margin-bottom: 14px;
    }
    .ais-input:focus, .ais-select:focus { outline: none; border-color: #7c3aed; }
    .ais-select { appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%2364748b' d='M1 1l5 5 5-5'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 10px center; padding-right: 28px; }

    .ais-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 4px; }
    .ais-status { font-size: 11px; color: #34d399; min-height: 14px; }
    .ais-actions { display: flex; gap: 7px; }
    .ais-cancel-btn {
      background: none; color: #64748b; border: 1px solid #2d3148;
      border-radius: 7px; padding: 6px 13px; font-size: 12px; cursor: pointer;
    }
    .ais-cancel-btn:hover { color: #94a3b8; }
    .ais-save-btn {
      background: #7c3aed; color: #fff; border: none;
      border-radius: 7px; padding: 6px 16px; font-size: 12px; font-weight: 700; cursor: pointer;
    }
    .ais-save-btn:hover { background: #6d28d9; }
  `;

  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ── HTML ────────────────────────────────────────────────────────────────
  const wrap = document.createElement('div');
  wrap.innerHTML = `
    <button id="ais-fab" title="AI Settings">&#9881;</button>

    <div id="ais-overlay"></div>

    <div id="ais-modal">
      <div class="ais-head">
        <span class="ais-title">&#9881; AI Settings</span>
        <button class="ais-close-btn" id="ais-close">&#10005;</button>
      </div>
      <div class="ais-sub">Default provider for all AI tasks</div>

      <div class="ais-toggle">
        <button id="ais-btn-claude" class="ais-tog-btn" onclick="window._aisSetProv('claude')">&#10022; Claude</button>
        <button id="ais-btn-ollama" class="ais-tog-btn" onclick="window._aisSetProv('ollama')">&#9672; Ollama</button>
        <button id="ais-btn-local-claude" class="ais-tog-btn" onclick="window._aisSetProv('local-claude')">&#9685; Local</button>
      </div>

      <div id="ais-sec-claude">
        <div class="ais-label">Anthropic API Key</div>
        <input type="password" id="ais-api-key" class="ais-input" placeholder="sk-ant-…" autocomplete="off" />
        <div class="ais-label">Model</div>
        <select id="ais-claude-model" class="ais-select">
          <option value="claude-sonnet-4-6">Sonnet 4.6 (Recommended)</option>
          <option value="claude-haiku-4-5-20251001">Haiku 4.5 (Fastest)</option>
        </select>
      </div>
      <div id="ais-sec-ollama" style="display:none">
        <div class="ais-label">Ollama Model</div>
        <select id="ais-model" class="ais-select"><option value="">Loading…</option></select>
      </div>
      <div id="ais-sec-local-claude" style="display:none">
        <div style="background:#0c1929;border:1px solid #0e3a52;border-radius:8px;padding:11px 13px;margin-bottom:14px;">
          <div style="font-size:12px;font-weight:700;color:#22d3ee;margin-bottom:4px;">&#9685; Local Claude Code</div>
          <div style="font-size:11px;color:#64748b;line-height:1.6;">Uses the <code style="color:#94a3b8">claude</code> CLI already running on this machine. No API key required — uses your authenticated session.</div>
        </div>
        <div class="ais-label">Model</div>
        <select id="ais-local-claude-model" class="ais-select">
          <option value="claude-sonnet-4-6">Sonnet 4.6 (Recommended)</option>
          <option value="claude-haiku-4-5-20251001">Haiku 4.5 (Fastest)</option>
        </select>
      </div>

      <div class="ais-footer">
        <div class="ais-status" id="ais-status"></div>
        <div class="ais-actions">
          <button class="ais-cancel-btn" id="ais-cancel">Cancel</button>
          <button class="ais-save-btn" id="ais-save">Save</button>
        </div>
      </div>
    </div>
  `;

  // ── State ────────────────────────────────────────────────────────────────
  let _prov = 'claude';

  // ── Mount after DOM ready ────────────────────────────────────────────────
  function mount() {
    document.body.appendChild(wrap);

    document.getElementById('ais-fab').addEventListener('click', _aisOpen);
    document.getElementById('ais-overlay').addEventListener('click', _aisClose);
    document.getElementById('ais-close').addEventListener('click', _aisClose);
    document.getElementById('ais-cancel').addEventListener('click', _aisClose);
    document.getElementById('ais-save').addEventListener('click', _aisSave);

    _aisRefreshFab();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }

  // ── Public API ───────────────────────────────────────────────────────────
  window._aisOpen = function () {
    _prov = localStorage.getItem('ai_provider') || 'claude';
    document.getElementById('ais-api-key').value = localStorage.getItem('claude_api_key') || '';
    const savedModel = localStorage.getItem('claude_model') || 'claude-sonnet-4-6';
    document.getElementById('ais-claude-model').value = savedModel;
    document.getElementById('ais-local-claude-model').value = savedModel;
    document.getElementById('ais-status').textContent = '';
    _aisSetProv(_prov);
    document.getElementById('ais-overlay').classList.add('open');
    document.getElementById('ais-modal').classList.add('open');
  };

  window._aisClose = function () {
    document.getElementById('ais-overlay').classList.remove('open');
    document.getElementById('ais-modal').classList.remove('open');
  };

  window._aisSetProv = function (p) {
    _prov = p;
    document.getElementById('ais-btn-claude').className      = 'ais-tog-btn ' + (p === 'claude'       ? 'on-claude'       : 'off');
    document.getElementById('ais-btn-ollama').className      = 'ais-tog-btn ' + (p === 'ollama'       ? 'on-ollama'       : 'off');
    document.getElementById('ais-btn-local-claude').className = 'ais-tog-btn ' + (p === 'local-claude' ? 'on-local-claude' : 'off');
    document.getElementById('ais-sec-claude').style.display       = p === 'claude'       ? '' : 'none';
    document.getElementById('ais-sec-ollama').style.display       = p === 'ollama'       ? '' : 'none';
    document.getElementById('ais-sec-local-claude').style.display = p === 'local-claude' ? '' : 'none';
    if (p === 'ollama') _aisLoadModels();
  };

  async function _aisLoadModels() {
    const sel = document.getElementById('ais-model');
    sel.innerHTML = '<option value="">Starting Ollama…</option>';
    try {
      const data = await (await fetch('/ollama/tags')).json();
      const models = (data.models || []).map(m => m.name);
      const saved = localStorage.getItem('ollama_model') || '';
      if (!models.length) {
        sel.innerHTML = '<option value="">No models installed</option>';
        return;
      }
      sel.innerHTML = models
        .map(m => `<option value="${m}"${m === saved ? ' selected' : ''}>${m}</option>`)
        .join('');
    } catch {
      sel.innerHTML = '<option value="">Ollama unavailable</option>';
    }
  }

  function _aisSave() {
    localStorage.setItem('ai_provider', _prov);

    if (_prov === 'claude') {
      const key = document.getElementById('ais-api-key').value.trim();
      if (key) localStorage.setItem('claude_api_key', key);
      const model = document.getElementById('ais-claude-model').value;
      if (model) localStorage.setItem('claude_model', model);
    } else if (_prov === 'ollama') {
      const model = document.getElementById('ais-model').value;
      if (model) localStorage.setItem('ollama_model', model);
    } else if (_prov === 'local-claude') {
      const model = document.getElementById('ais-local-claude-model').value;
      if (model) localStorage.setItem('claude_model', model);
    }

    _aisRefreshFab();

    // Notify pages so they can sync live state
    document.dispatchEvent(new CustomEvent('aisettings:changed', {
      detail: { provider: _prov }
    }));

    document.getElementById('ais-status').textContent = '✓ Saved';
    setTimeout(_aisClose, 750);
  }

  function _aisRefreshFab() {
    const p = localStorage.getItem('ai_provider') || 'claude';
    const fab = document.getElementById('ais-fab');
    if (!fab) return;
    fab.className = '';
    fab.id = 'ais-fab';
    const cls = p === 'ollama' ? 'prov-ollama' : p === 'local-claude' ? 'prov-local-claude' : 'prov-claude';
    fab.classList.add(cls);
  }

  // Public-demo mode: hide controls for server-disabled actions (generation,
  // Python terminal, program/domain/module/lesson creation). Server also 403s them.
  fetch('/app_config').then(r => r.json()).then(c => {
    if (!c || !c.demo_mode) return;
    document.body.classList.add('demo-mode');
    const s = document.createElement('style');
    s.textContent = 'body.demo-mode #generateBtn,body.demo-mode #py-terminal,'
      + 'body.demo-mode #add-tile,body.demo-mode .tab-add,body.demo-mode .gen-first-btn,'
      + 'body.demo-mode .add-mod-btn,body.demo-mode .add-lesson-btn{display:none !important;}';
    document.head.appendChild(s);
  }).catch(() => {});
})();
