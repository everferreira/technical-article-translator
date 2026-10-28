/* ── Technical Article Translator — JavaScript ───────────────────── */

(function () {
  'use strict';

  // ── Estado ──────────────────────────────────────────
  const state = {
    source: 'auto',
    target: 'pt',
    mode: 'technical',
    translating: false,
  };

  // ── IDs dos idiomas MyMemory ────────────────────────
  // MyMemory usa códigos ISO 639-1 (mesmo do Google Translate)
  const LANGUAGES = [
    { code: 'auto', name: 'Detectar idioma' },
    { code: 'en', name: 'English' },
    { code: 'pt', name: 'Português' },
    { code: 'es', name: 'Español' },
    { code: 'fr', name: 'Français' },
    { code: 'de', name: 'Deutsch' },
    { code: 'it', name: 'Italiano' },
    { code: 'nl', name: 'Nederlands' },
    { code: 'ja', name: '日本語' },
    { code: 'zh', name: '中文' },
    { code: 'ru', name: 'Русский' },
    { code: 'ko', name: '한국어' },
    { code: 'ar', name: 'العربية' },
    { code: 'hi', name: 'हिन्दी' },
    { code: 'tr', name: 'Türkçe' },
    { code: 'pl', name: 'Polski' },
    { code: 'sv', name: 'Svenska' },
    { code: 'da', name: 'Dansk' },
    { code: 'fi', name: 'Suomi' },
    { code: 'nb', name: 'Norsk' },
    { code: 'cs', name: 'Čeština' },
    { code: 'ro', name: 'Română' },
    { code: 'th', name: 'ไทย' },
    { code: 'vi', name: 'Tiếng Việt' },
    { code: 'id', name: 'Bahasa Indonesia' },
    { code: 'ms', name: 'Bahasa Melayu' },
  ];

  // ── Termos técnicos protegidos (preservados na tradução) ─
  const TECH_TERMS = new Set([
    'Python', 'Java', 'JavaScript', 'TypeScript', 'C#', 'C++', 'Rust', 'Go',
    'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'Perl', 'Lua', 'Elixir',
    'Node\\.js', 'Deno', '\\.NET', 'React', 'Angular', 'Vue', 'Flask', 'FastAPI',
    'Django', 'Spring Boot', 'Next\\.js', 'Tailwind', 'Bootstrap',
    'Azure', 'AWS', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Ansible',
    'CI/CD', 'GitHub Actions', 'GitLab CI', 'Jenkins',
    'API', 'REST', 'GraphQL', 'JSON', 'YAML', 'SQL', 'NoSQL', 'LLM',
    'GPT', 'Transformers', 'TensorFlow', 'PyTorch', 'scikit-learn',
    'Pandas', 'NumPy', 'OpenAI', 'LangChain',
    'Git', 'Linux', 'HTTP', 'HTTPS', 'SSH', 'CLI', 'SDK', 'IDE',
    'CRUD', 'JWT', 'OAuth', 'WebSocket', 'gRPC',
    'AWS Lambda', 'Azure Functions', 'Serverless', 'Microservices',
  ]);

  // ── Elementos DOM ───────────────────────────────────
  const els = {};

  function initDOM() {
    els.inputText = document.getElementById('input-text');
    els.outputText = document.getElementById('output-text');
    els.sourceSelect = document.getElementById('source-lang');
    els.targetSelect = document.getElementById('target-lang');
    els.swapBtn = document.getElementById('swap-langs');
    els.modeBtns = document.querySelectorAll('.mode-btn');
    els.modeDesc = document.getElementById('mode-desc');
    els.translateBtn = document.getElementById('translate-btn');
    els.clearBtn = document.getElementById('clear-btn');
    els.copyBtn = document.getElementById('copy-btn');
    els.statusBar = document.getElementById('status-bar');
    els.inputChars = document.getElementById('input-chars');
  }

  // ── Popular selects ─────────────────────────────────
  function populateSelects() {
    const toExclude = new Set(['auto']);
    LANGUAGES.forEach(lang => {
      // Source: inclui 'auto'
      const srcOpt = document.createElement('option');
      srcOpt.value = lang.code;
      srcOpt.textContent = lang.code === 'auto' ? '🌐 Detectar' : `${lang.name} (${lang.code})`;
      if (lang.code === state.source) srcOpt.selected = true;
      els.sourceSelect.appendChild(srcOpt);

      // Target: exclui 'auto'
      if (!toExclude.has(lang.code)) {
        const tgtOpt = document.createElement('option');
        tgtOpt.value = lang.code;
        tgtOpt.textContent = `${lang.name} (${lang.code})`;
        if (lang.code === state.target) tgtOpt.selected = true;
        els.targetSelect.appendChild(tgtOpt);
      }
    });
  }

  // ── Modo de tradução ────────────────────────────────
  function initModeToggle() {
    els.modeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        els.modeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.mode = btn.dataset.mode;
        const descs = {
          technical: '🔧 Preserva blocos de código, termos técnicos (API, Docker, Python...) e URLs',
          general: '📝 Tradução direta sem preservação especializada',
        };
        els.modeDesc.textContent = descs[state.mode] || '';
      });
    });
  }

  // ── Swap idiomas ────────────────────────────────────
  function initSwap() {
    els.swapBtn.addEventListener('click', () => {
      const src = els.sourceSelect.value;
      const tgt = els.targetSelect.value;
      if (src === 'auto') return; // não swappa source=auto
      els.sourceSelect.value = tgt;
      els.targetSelect.value = src;
      state.source = tgt;
      state.target = src;
    });

    els.sourceSelect.addEventListener('change', () => {
      state.source = els.sourceSelect.value;
    });
    els.targetSelect.addEventListener('change', () => {
      state.target = els.targetSelect.value;
    });
  }

  // ── Contagem de caracteres ──────────────────────────
  function initCharCount() {
    els.inputText.addEventListener('input', () => {
      const len = els.inputText.value.length;
      els.inputChars.textContent = `${len.toLocaleString()} chars`;
      els.translateBtn.disabled = len === 0;
    });
  }

  // ── Textarea tab → indent ───────────────────────────
  function initTextareaTabs() {
    const ta = els.inputText;
    ta.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = ta.selectionStart;
        ta.value = ta.value.substring(0, start) + '  ' + ta.value.substring(ta.selectionEnd);
        ta.selectionStart = ta.selectionEnd = start + 2;
      }
    });
  }

  // ── Tradutor com placeholders (modo técnico) ────────
  // Versão client-side: usa MyMemory API (gratuita)
  // O modo técnico é implementado com pré/pós-processamento

  const PH = {
    _idx: 0,
    _blocks: [],

    reset() {
      this._idx = 0;
      this._blocks = [];
    },

    // Preserva blocos de código ```...```
    protectCodeBlocks(text) {
      return text.replace(/```[\w]*\n[\s\S]*?```/g, (match) => {
        const ph = `__CB_${this._idx}__`;
        this._blocks.push({ type: 'codeblock', ph, original: match });
        this._idx++;
        return ph;
      });
    },

    // Preserva código inline `...`
    protectInlineCode(text) {
      return text.replace(/`[^`]+`/g, (match) => {
        const ph = `__IC_${this._idx}__`;
        this._blocks.push({ type: 'inlinecode', ph, original: match });
        this._idx++;
        return ph;
      });
    },

    // Preserva URLs
    protectURLs(text) {
      return text.replace(/https?:\/\/\S+/g, (match) => {
        const ph = `__URL_${this._idx}__`;
        this._blocks.push({ type: 'url', ph, original: match });
        this._idx++;
        return ph;
      });
    },

    // Preserva termos técnicos
    protectTerms(text) {
      const terms = [...TECH_TERMS].sort((a, b) => b.length - a.length);
      const escaped = terms.map(t => ({ pattern: t, original: t }));
      let result = text;
      for (const { pattern, original } of escaped) {
        const re = new RegExp(`\\b${pattern}\\b`, 'g');
        result = result.replace(re, (match) => {
          const ph = `__TECH_${this._idx}__`;
          this._blocks.push({ type: 'term', ph, original: match });
          this._idx++;
          return ph;
        });
      }
      return result;
    },

    // Restaura todos os placeholders
    restore(text) {
      // Ordem inversa para não conflitar
      const sorted = [...this._blocks].reverse();
      for (const block of sorted) {
        text = text.replace(block.ph, block.original);
      }
      return text;
    },
  };

  // ── Chamada à MyMemory API ─────────────────────────
  async function translateMyMemory(text, source, target) {
    const params = new URLSearchParams({
      q: text,
      langpair: `${source === 'auto' ? 'en' : source}|${target}`,
    });

    const url = `https://api.mymemory.translated.net/get?${params}`;

    const resp = await fetch(url, {
      headers: { 'User-Agent': 'TechnicalArticleTranslator/1.0' },
    });

    if (!resp.ok) {
      throw new Error(`API error ${resp.status}: ${resp.statusText}`);
    }

    const data = await resp.json();
    if (data.responseStatus !== 200) {
      throw new Error(`MyMemory error ${data.responseStatus}: ${data.responseDetails || 'unknown'}`);
    }

    return data.responseData.translatedText;
  }

  // ── Traduzir ────────────────────────────────────────
  async function translate() {
    const text = els.inputText.value;
    if (!text.trim()) {
      setStatus('Digite um texto para traduzir', '');
      return;
    }

    if (state.translating) return;

    state.translating = true;
    els.translateBtn.disabled = true;
    els.translateBtn.innerHTML = '<span class="spinner">⟳</span> Traduzindo...';
    setStatus('Traduzindo...', '');

    try {
      let processed = text;
      let translated;

      if (state.mode === 'technical') {
        PH.reset();
        processed = PH.protectCodeBlocks(processed);
        processed = PH.protectInlineCode(processed);
        processed = PH.protectURLs(processed);
        processed = PH.protectTerms(processed);

        translated = await translateMyMemory(processed, state.source, state.target);

        translated = PH.restore(translated);
      } else {
        translated = await translateMyMemory(processed, state.source, state.target);
      }

      els.outputText.value = translated;
      setStatus('✔ Tradução concluída', 'success');
      updateCopyButton();
    } catch (err) {
      console.error('Translation error:', err);
      setStatus(`✖ Erro: ${err.message}`, 'error');
      // Fallback: mostra o texto original
      if (!els.outputText.value) {
        els.outputText.value = text;
      }
    } finally {
      state.translating = false;
      els.translateBtn.disabled = false;
      els.translateBtn.innerHTML = '🌐 Traduzir Artigo';
    }
  }

  // ── Status ──────────────────────────────────────────
  function setStatus(msg, type) {
    els.statusBar.textContent = msg;
    els.statusBar.className = type ? type : '';
  }

  // ── Copy button ─────────────────────────────────────
  function updateCopyButton() {
    const hasText = els.outputText.value.trim().length > 0;
    els.copyBtn.style.display = hasText ? '' : 'none';
  }

  function initCopy() {
    els.copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(els.outputText.value);
        showToast('📋 Copiado para a área de transferência!');
      } catch {
        // fallback
        els.outputText.select();
        document.execCommand('copy');
        showToast('📋 Copiado!');
      }
    });
  }

  // ── Clear ───────────────────────────────────────────
  function initClear() {
    els.clearBtn.addEventListener('click', () => {
      els.inputText.value = '';
      els.outputText.value = '';
      els.inputChars.textContent = '0 chars';
      els.translateBtn.disabled = true;
      els.copyBtn.style.display = 'none';
      setStatus('', '');
    });
  }

  // ── Toast ───────────────────────────────────────────
  function showToast(msg, type) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = 'toast' + (type === 'error' ? ' error' : '');
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), 2500);
  }

  // ── Exemplo de artigo (preencher para teste) ────────
  function loadExample() {
    const example = `# Getting Started with Docker Containers

## Introduction

Docker is a platform that enables **containerization** — a lightweight form of virtualization where applications run in isolated environments called *containers*. Unlike traditional virtual machines, Docker containers share the host OS kernel, making them faster and more efficient.

## Key Concepts

### Images and Containers

A \`Docker image\` is a read-only template with instructions to create a container. When you run an image, it becomes a **container** — a running instance of that image.

\`\`\`bash
# Pull an image from Docker Hub
docker pull python:3.12-slim

# Run a container
docker run -it --name myapp python:3.12-slim bash
\`\`\`

### Dockerfile

A Dockerfile is a script with instructions to build an image:

\`\`\`dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
\`\`\`

## Best Practices

- Use **multi-stage builds** to keep images small
- Leverage Docker's **layer cache** by copying dependency files first
- Run containers with **least privilege** — avoid \`--privileged\` flag
- Use **Docker Compose** for multi-service applications

## Conclusion

Docker revolutionized DevOps by making \`"it works on my machine"\` a thing of the past. With containerization, you get consistent environments from development to production.`;

    els.inputText.value = example;
    els.inputChars.textContent = `${example.length.toLocaleString()} chars`;
    els.translateBtn.disabled = false;
    setStatus('📄 Exemplo carregado! Clique em "Traduzir"', '');
  }

  // ── Init ────────────────────────────────────────────
  function init() {
    initDOM();
    populateSelects();
    initModeToggle();
    initSwap();
    initCharCount();
    initTextareaTabs();
    initCopy();
    initClear();

    // Translate button
    els.translateBtn.addEventListener('click', translate);

    // Keyboard shortcut: Ctrl+Enter
    els.inputText.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        translate();
      }
    });

    // Example button
    document.getElementById('example-btn')?.addEventListener('click', loadExample);

    // Initial state
    els.translateBtn.disabled = true;
    els.copyBtn.style.display = 'none';

    // Mode description
    els.modeDesc.textContent = '🔧 Preserva blocos de código, termos técnicos (API, Docker, Python...) e URLs';
  }

  // ── Start ───────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', init);
})();