// Prototype: each tradition column has two faces, original and English.
(() => {
  const mode = document.body.dataset.proto;
  const LANGS = ['pi', 'pd', 'ga', 'sa', 'zh', 'bo'];
  const editions = JSON.parse(document.getElementById('english-editions')?.textContent || '{}');
  editions.pi = JSON.parse(document.getElementById('pi-english').textContent);
  const esc = s => s.replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  const NAMES = {pi: 'Pāli', pd: 'Patna', ga: 'Gāndhārī', sa: 'Sanskrit', zh: 'Chinese', bo: 'Tibetan'};

  // The English column is fixed to the Pāli-based translation in this model; the menu retires.
  const select = document.getElementById('english-source');
  if (select) {
    const label = select.closest('.english-source');
    const fixed = document.createElement('span');
    fixed.className = 'column-reference';
    fixed.textContent = 'Rosettapada · from the Pāli';
    label.replaceWith(fixed);
    document.querySelectorAll('.verse .lang-en .poem').forEach(poem => {
      const n = poem.closest('.verse').dataset.verse;
      poem.innerHTML = (editions.pi[n] || []).map(l => `<span class="poem-line">${esc(l)}</span>`).join('');
    });
  }

  const cells = [];
  document.querySelectorAll('.verse').forEach(verse => {
    verse.querySelectorAll('.witness').forEach(w => {
      const lang = w.dataset.language;
      const poem = w.querySelector('.poem');
      if (!LANGS.includes(lang) || !poem) return;
      cells.push({w, poem, lang, n: verse.dataset.verse, verse, original: poem.innerHTML, face: 'orig'});
    });
  });
  const heads = new Map(Array.from(document.querySelectorAll('.column-heading')).map(h => [h.dataset.language, h]));

  function paint(cell, face) {
    const lines = editions[cell.lang]?.[cell.n];
    cell.w.classList.remove('face-en', 'face-both');
    if (face === 'orig' || !lines) { cell.poem.innerHTML = cell.original; return; }
    if (face === 'en') {
      cell.w.classList.add('face-en');
      cell.poem.innerHTML = lines.map(l => `<span class="poem-line">${esc(l)}</span>`).join('');
      return;
    }
    cell.w.classList.add('face-both');
    const tmp = document.createElement('div');
    tmp.innerHTML = cell.original;
    const orig = Array.from(tmp.querySelectorAll('.poem-line'));
    if (orig.length === lines.length) {
      cell.poem.innerHTML = orig.map((o, i) => o.outerHTML + `<span class="gloss">${esc(lines[i])}</span>`).join('');
    } else {
      cell.poem.innerHTML = cell.original + `<span class="gloss-block">${lines.map(l => `<span class="gloss">${esc(l)}</span>`).join('')}</span>`;
    }
  }
  const columnFace = new Map(LANGS.map(l => [l, 'orig']));
  // A column showing English needs room for English line lengths.
  function widen(lang, face) {
    const head = heads.get(lang);
    if (!head) return;
    head.dataset.origWidth ??= head.dataset.width;
    head.dataset.width = face === 'orig' ? head.dataset.origWidth : `max(${head.dataset.origWidth}, ${face === 'en' ? '420px' : '390px'})`;
  }
  function relayout() {
    const visible = Array.from(document.querySelectorAll('#column-headings > .column-heading')).filter(h => !h.hidden);
    document.getElementById('sheet').style.setProperty('--columns', visible.map(h => h.dataset.width).join(' '));
  }
  function setColumn(lang, face) {
    columnFace.set(lang, face);
    widen(lang, face);
    relayout();
    cells.filter(c => c.lang === lang).forEach(c => { c.face = face; paint(c, face); });
    const head = heads.get(lang);
    if (head) {
      head.classList.toggle('head-en', face !== 'orig');
      const tag = head.querySelector('.face-tag');
      if (tag) tag.textContent = face === 'en' ? 'in English' : face === 'both' ? 'with English' : '';
      const toggle = head.querySelector('.face-toggle');
      if (toggle) toggle.setAttribute('aria-pressed', String(face !== 'orig'));
    }
  }
  heads.forEach((head, lang) => {
    if (!LANGS.includes(lang)) return;
    const tag = document.createElement('span');
    tag.className = 'face-tag';
    head.querySelector('.column-name').append(tag);
  });

  // Hiding the dedicated English column when every column already shows English,
  // without leaking the choice into the real site's saved layout.
  const layoutKey = 'rosettapada-languages-historical-v1';
  function englishColumn(show) {
    const before = localStorage.getItem(layoutKey);
    const hidden = Boolean(document.querySelector('.column-show[data-language="en"]'));
    if (show && hidden) document.querySelector('.column-show[data-language="en"]')?.click();
    else if (!hidden) heads.get('en')?.querySelector('.column-hide')?.click();
    if (before === null) localStorage.removeItem(layoutKey); else localStorage.setItem(layoutKey, before);
  }

  function segmented(options, onPick, initial) {
    const box = document.createElement('div');
    box.className = 'face-switch';
    box.setAttribute('role', 'radiogroup');
    box.setAttribute('aria-label', 'Show texts as');
    options.forEach(([value, label]) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = label;
      b.setAttribute('role', 'radio');
      b.dataset.value = value;
      b.setAttribute('aria-checked', String(value === initial));
      b.addEventListener('click', () => {
        box.querySelectorAll('button').forEach(x => x.setAttribute('aria-checked', String(x === b)));
        onPick(value);
      });
      box.append(b);
    });
    const nav = document.querySelector('.top-nav');
    nav.insertBefore(box, nav.firstChild);
    return box;
  }
  let globalFace = 'orig';
  function setAll(face) {
    globalFace = face;
    LANGS.forEach(l => setColumn(l, face));
    englishColumn(face !== 'en');
  }

  if (mode === 'sheet') segmented([['orig', 'Original'], ['en', 'English']], setAll, 'orig');
  if (mode === 'interlinear') segmented([['orig', 'Original'], ['both', 'Both'], ['en', 'English']], setAll, 'orig');

  if (mode === 'column' || mode === 'interlinear') {
    heads.forEach((head, lang) => {
      if (!LANGS.includes(lang)) return;
      const ref = head.querySelector('.column-reference');
      const t = document.createElement('button');
      t.type = 'button';
      t.className = 'face-toggle';
      t.setAttribute('aria-pressed', 'false');
      t.title = `Show ${NAMES[lang]} in English`;
      t.innerHTML = `<span class="face-orig">${NAMES[lang]}</span><span class="face-en-label">EN</span>`;
      t.addEventListener('pointerdown', e => e.stopPropagation());
      t.addEventListener('click', e => {
        e.stopPropagation();
        setColumn(lang, columnFace.get(lang) === 'orig' ? (globalFace === 'both' ? 'both' : 'en') : 'orig');
      });
      (ref || head.querySelector('.column-name')).after(t);
    });
  }

  if (mode === 'verse') {
    document.querySelectorAll('.verse').forEach(verse => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'verse-lens';
      b.setAttribute('aria-pressed', 'false');
      b.title = 'Show this verse in English across every tradition';
      b.textContent = 'EN';
      b.addEventListener('click', () => {
        const on = b.getAttribute('aria-pressed') !== 'true';
        b.setAttribute('aria-pressed', String(on));
        verse.classList.toggle('verse-open', on);
        cells.filter(c => c.verse === verse).forEach(c => paint(c, on ? 'both' : 'orig'));
        const anyOpen = Boolean(document.querySelector('.verse-open'));
        LANGS.forEach(l => widen(l, anyOpen ? 'both' : 'orig'));
        relayout();
      });
      verse.prepend(b);
    });
  }

  // Peek: hold E to see every column in English; let go to return.
  let peeking = false;
  const typing = el => el && (el.isContentEditable || /^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName));
  document.addEventListener('keydown', e => {
    if ((e.key === 'e' || e.key === 'E') && !e.repeat && !peeking && !typing(e.target) && !e.metaKey && !e.ctrlKey) {
      peeking = true;
      document.body.classList.add('peeking');
      cells.forEach(c => paint(c, 'en'));
      LANGS.forEach(l => widen(l, 'en'));
      relayout();
    }
  });
  const endPeek = () => {
    if (!peeking) return;
    peeking = false;
    document.body.classList.remove('peeking');
    cells.forEach(c => paint(c, c.verse.classList.contains('verse-open') ? 'both' : c.face));
    LANGS.forEach(l => widen(l, columnFace.get(l)));
    relayout();
  };
  document.addEventListener('keyup', e => { if (e.key === 'e' || e.key === 'E') endPeek(); });
  window.addEventListener('blur', endPeek);
})();
