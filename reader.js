/* Rosettapada: native scrolling, selectable text, and one continuously scaled sheet. */
(() => {
  'use strict';
  const viewport = document.getElementById('viewport');
  if (!viewport) return;
  const sheet = document.getElementById('sheet');
  const headings = document.getElementById('column-headings');
  const verses = Array.from(sheet.querySelectorAll('.verse'));
  const previousVerse = document.getElementById('previous-verse');
  const nextVerse = document.getElementById('next-verse');
  const label = document.getElementById('location');
  const zoomLabel = document.getElementById('zoom-label');
  const announcement = document.getElementById('zoom-announcement');
  const help = document.getElementById('reading-help');
  const settings = document.getElementById('reading-settings');
  const settingsButton = document.getElementById('open-settings');
  const options = document.getElementById('language-options');
  const settingsAnnouncement = document.getElementById('settings-announcement');
  const columnHeads = Array.from(headings.children);
  const defaultOrder = columnHeads.map(column => column.dataset.language);
  const columnByKey = new Map(columnHeads.map(column => [column.dataset.language, column]));
  const rowsByKey = new Map(Array.from(options.children).map(row => [row.dataset.language, row]));
  const groups = [headings, ...document.querySelectorAll('.verse-grid')];
  const groupColumns = groups.map(group => new Map(Array.from(group.children).map(column => [column.dataset.language, column])));
  const minZoom = .1;
  const maxZoom = 3;
  const isChapter = sheet.dataset.profile !== 'sample';
  const storageKey = isChapter ? `rosettapada-reading-v5-${sheet.dataset.pageKey}` : 'rosettapada-reading-v4';
  const languageStorageKey = isChapter ? 'rosettapada-languages-historical-v1' : 'rosettapada-languages-v1';
  const previousPage = sheet.dataset.previousPage;
  const nextPage = sheet.dataset.nextPage;
  const clamp = (n, min, max) => Math.min(max, Math.max(min, n));
  let zoom = 1;
  let active = 0;
  let spaceHeld = false;
  let dragging = null;
  let safariGesture = null;
  let touchGesture = null;
  let frame = 0;
  let saveTimer;
  let announcementTimer;
  let fitMode = false;
  let languageOrder = defaultOrder.slice();
  let hiddenLanguages = new Set(defaultOrder.filter(key => key === 'zh-pinyin'));
  let languageDrag = null;

  try {
    const saved = JSON.parse(localStorage.getItem(languageStorageKey));
    if (saved && Array.isArray(saved.order)) languageOrder = Array.from(new Set([...saved.order.filter(key => defaultOrder.includes(key)), ...defaultOrder]));
    if (saved && Array.isArray(saved.hidden)) hiddenLanguages = new Set(saved.hidden.filter(key => defaultOrder.includes(key)));
    if (hiddenLanguages.size === defaultOrder.length) hiddenLanguages.delete('en');
  } catch { /* Defaults work when storage is unavailable or its contents are invalid. */ }

  function saveLanguages() {
    try { localStorage.setItem(languageStorageKey, JSON.stringify({order: languageOrder, hidden: Array.from(hiddenLanguages)})); }
    catch { /* Settings still apply for this visit. */ }
  }
  function orderChildren(parent, elements) {
    languageOrder.forEach((key, index) => {
      const element = elements.get(key);
      if (parent.children[index] !== element) parent.insertBefore(element, parent.children[index] || null);
    });
  }
  function applyLanguages(preservePosition = true) {
    const oldTop = verses[active].getBoundingClientRect().top;
    const oldLeft = viewport.scrollLeft;
    const visible = languageOrder.filter(key => !hiddenLanguages.has(key));
    sheet.style.setProperty('--columns', visible.map(key => columnByKey.get(key).dataset.width).join(' '));
    groups.forEach((group, index) => {
      groupColumns[index].forEach((element, key) => { element.hidden = hiddenLanguages.has(key); });
      orderChildren(group, groupColumns[index]);
    });
    orderChildren(options, rowsByKey);
    rowsByKey.forEach((row, key) => {
      const checkbox = row.querySelector('input');
      checkbox.checked = !hiddenLanguages.has(key);
      checkbox.disabled = visible.length === 1 && checkbox.checked;
      checkbox.title = checkbox.disabled ? 'Keep at least one column visible' : '';
    });
    updateTail();
    if (preservePosition) {
      viewport.scrollTop += verses[active].getBoundingClientRect().top - oldTop;
      viewport.scrollLeft = oldLeft;
      if (fitMode) fitSheet();
      saveLanguages();
      scheduleNavigation();
    }
  }
  function moveLanguage(key, delta) {
    const from = languageOrder.indexOf(key);
    const to = clamp(from + delta, 0, languageOrder.length - 1);
    if (from < 0 || from === to) return;
    languageOrder.splice(from, 1);
    languageOrder.splice(to, 0, key);
    applyLanguages();
    rowsByKey.get(key).querySelector('.drag-handle').focus({preventScroll: true});
    settingsAnnouncement.textContent = `${columnByKey.get(key).querySelector('.column-name').textContent} moved to position ${to + 1}`;
  }
  options.addEventListener('change', event => {
    const checkbox = event.target.closest('input[data-language]');
    if (!checkbox) return;
    if (checkbox.checked) hiddenLanguages.delete(checkbox.dataset.language);
    else hiddenLanguages.add(checkbox.dataset.language);
    applyLanguages();
  });
  // Labels keep the checkbox's accessible name, but the rest of a row is a drag surface.
  options.addEventListener('click', event => {
    if (event.target.closest('.language-option') && !event.target.closest('input[type="checkbox"]')) event.preventDefault();
  });
  options.addEventListener('keydown', event => {
    const handle = event.target.closest('.drag-handle');
    if (!handle || !['ArrowUp', 'ArrowDown'].includes(event.key)) return;
    event.preventDefault();
    moveLanguage(handle.dataset.language, event.key === 'ArrowUp' ? -1 : 1);
  });
  function clearLanguageDrag() {
    const pointerId = languageDrag?.pointerId;
    languageDrag = null;
    options.classList.remove('is-reordering');
    rowsByKey.forEach(row => row.classList.remove('is-dragging', 'drop-before', 'drop-after'));
    if (pointerId !== undefined && options.hasPointerCapture(pointerId)) options.releasePointerCapture(pointerId);
  }
  options.addEventListener('pointerdown', event => {
    const row = event.target.closest('.language-option');
    if (!row || event.target.closest('input[type="checkbox"]') || event.button !== 0) return;
    event.preventDefault();
    row.querySelector('.drag-handle').focus({preventScroll: true});
    languageDrag = {key: row.dataset.language, pointerId: event.pointerId, x: event.clientX, y: event.clientY, started: false, before: null};
    options.setPointerCapture(event.pointerId);
  });
  options.addEventListener('pointermove', event => {
    if (!languageDrag || languageDrag.pointerId !== event.pointerId) return;
    if (!languageDrag.started && Math.hypot(event.clientX - languageDrag.x, event.clientY - languageDrag.y) < 4) return;
    languageDrag.started = true;
    options.classList.add('is-reordering');
    rowsByKey.get(languageDrag.key).classList.add('is-dragging');
    rowsByKey.forEach(row => row.classList.remove('drop-before', 'drop-after'));
    const before = Array.from(options.children).find(row => {
      if (row.dataset.language === languageDrag.key) return false;
      const rect = row.getBoundingClientRect();
      return event.clientY < rect.top + rect.height / 2;
    });
    languageDrag.before = before?.dataset.language || null;
    if (before) before.classList.add('drop-before');
    else options.lastElementChild.classList.add('drop-after');
  });
  options.addEventListener('pointerup', event => {
    if (!languageDrag || languageDrag.pointerId !== event.pointerId) return;
    const drag = languageDrag;
    const rect = options.getBoundingClientRect();
    const inside = event.clientX >= rect.left - 24 && event.clientX <= rect.right + 24 && event.clientY >= rect.top - 24 && event.clientY <= rect.bottom + 24;
    clearLanguageDrag();
    if (!drag.started || !inside) return;
    languageOrder = languageOrder.filter(key => key !== drag.key);
    const index = drag.before === null ? languageOrder.length : languageOrder.indexOf(drag.before);
    languageOrder.splice(index, 0, drag.key);
    applyLanguages();
    rowsByKey.get(drag.key).querySelector('.drag-handle').focus({preventScroll: true});
    settingsAnnouncement.textContent = 'Column order updated';
  });
  options.addEventListener('pointercancel', clearLanguageDrag);
  options.addEventListener('lostpointercapture', clearLanguageDrag);
  document.getElementById('restore-languages').addEventListener('click', () => {
    languageOrder = defaultOrder.slice();
    hiddenLanguages = new Set(defaultOrder.filter(key => key === 'zh-pinyin'));
    applyLanguages();
    settingsAnnouncement.textContent = 'Default languages and order restored';
  });
  function closeSettings() { settings.close(); settingsButton.focus({preventScroll: true}); }
  settingsButton.addEventListener('click', () => {
    if (settings.open) closeSettings();
    else { releasePan(); settings.show(); settingsButton.setAttribute('aria-expanded', 'true'); }
  });
  document.getElementById('close-settings').addEventListener('click', closeSettings);
  settings.addEventListener('close', () => settingsButton.setAttribute('aria-expanded', 'false'));

  function readPosition() {
    try { return JSON.parse(sessionStorage.getItem(storageKey)) || {}; }
    catch { return {}; }
  }
  function savePosition() {
    try {
      sessionStorage.setItem(storageKey, JSON.stringify({zoom, left: viewport.scrollLeft, top: viewport.scrollTop, verse: active}));
    } catch { /* Reading still works when browser storage is unavailable. */ }
  }
  function scheduleSave() { clearTimeout(saveTimer); saveTimer = setTimeout(savePosition, 160); }
  function updateTail() {
    // Leave enough paper after the sample to bring its final verse up to the reading line.
    sheet.style.paddingBottom = `${Math.max(160, viewport.clientHeight / zoom - 220)}px`;
  }
  function announceZoom() {
    clearTimeout(announcementTimer);
    announcementTimer = setTimeout(() => { announcement.textContent = `Sheet magnification ${Math.round(zoom * 100)} percent`; }, 180);
  }
  function updateNavigation(index) {
    active = clamp(index, 0, verses.length - 1);
    previousVerse.disabled = active === 0 && !previousPage;
    nextVerse.disabled = active === verses.length - 1 && !nextPage;
    const text = sheet.dataset.chapterTitle ? `Verse ${verses[active].dataset.verse}, ${sheet.dataset.chapterTitle}` : `Verse ${verses[active].dataset.verse} of ${verses.length}`;
    if (label.textContent !== text) label.textContent = text;
  }
  function readingTop() {
    return viewport.getBoundingClientRect().top + headings.getBoundingClientRect().height + 16 * zoom;
  }
  function syncNavigation() {
    frame = 0;
    const top = readingTop();
    let current = 0;
    verses.forEach((verse, index) => {
      if (verse.getBoundingClientRect().top <= top + 1) current = index;
    });
    updateNavigation(current);
    scheduleSave();
  }
  function scheduleNavigation() { if (!frame) frame = requestAnimationFrame(syncNavigation); }

  // CSS zoom keeps glyphs crisp and lets native scrolling use the scaled layout.
  // Disable browser scroll anchoring in CSS, then preserve the content point beneath the pointer.
  function setZoom(factor, clientX, clientY, mode = 'manual') {
    if (!Number.isFinite(factor)) return;
    fitMode = mode === 'fit';
    document.getElementById('fit-sheet').setAttribute('aria-pressed', String(fitMode));
    const target = clamp(factor, minZoom, maxZoom);
    if (Math.abs(target - zoom) < .0001) return;
    const rect = viewport.getBoundingClientRect();
    const x = clamp((clientX ?? rect.left + rect.width / 2) - rect.left, 0, viewport.clientWidth);
    const y = clamp((clientY ?? rect.top + rect.height / 2) - rect.top, 0, viewport.clientHeight);
    const sheetX = (viewport.scrollLeft + x) / zoom;
    const sheetY = (viewport.scrollTop + y) / zoom;
    zoom = target;
    sheet.style.zoom = String(zoom);
    updateTail();
    viewport.scrollLeft = sheetX * zoom - x;
    viewport.scrollTop = sheetY * zoom - y;
    zoomLabel.value = `${Math.round(zoom * 100)}%`;
    document.getElementById('zoom-out').disabled = zoom <= minZoom + .0001;
    document.getElementById('zoom-in').disabled = zoom >= maxZoom - .0001;
    scheduleNavigation();
    announceZoom();
    scheduleSave();
  }
  function goTo(index, historyMode = 'push') {
    const adjacentPage = index < 0 ? previousPage : index >= verses.length ? nextPage : '';
    if (adjacentPage) {
      savePosition();
      const pageKey = adjacentPage.split('#')[0].replace(/\.html$/, '');
      try {
        sessionStorage.setItem(`rosettapada-reading-v5-${pageKey}`, JSON.stringify({zoom, left: viewport.scrollLeft, top: 0}));
      } catch { /* The chapter link still works when browser storage is unavailable. */ }
      location.assign(adjacentPage);
      return;
    }
    const target = clamp(index, 0, verses.length - 1);
    const left = viewport.scrollLeft;
    const offset = verses[target].getBoundingClientRect().top - readingTop();
    viewport.scrollTop += offset;
    viewport.scrollLeft = left;
    updateNavigation(target);
    const hash = `#${verses[target].id}`;
    if (historyMode !== 'none' && location.hash !== hash) {
      try { history[historyMode === 'replace' ? 'replaceState' : 'pushState'](null, '', hash); } catch { /* Local file preview may restrict history. */ }
    }
    savePosition();
  }
  function hashIndex() { return verses.findIndex(verse => `#${verse.id}` === location.hash); }
  previousVerse.addEventListener('click', () => goTo(active - 1));
  nextVerse.addEventListener('click', () => goTo(active + 1));
  document.getElementById('zoom-out').addEventListener('click', () => setZoom(zoom / 1.18));
  document.getElementById('zoom-in').addEventListener('click', () => setZoom(zoom * 1.18));
  document.getElementById('reset-zoom').addEventListener('click', () => setZoom(1));
  function fitSheet() { setZoom(Math.min(1, viewport.clientWidth / sheet.offsetWidth), undefined, undefined, 'fit'); }
  document.getElementById('fit-sheet').addEventListener('click', fitSheet);
  viewport.addEventListener('scroll', scheduleNavigation, {passive: true});

  // Chromium reports a trackpad pinch as ctrl+wheel; ordinary wheel events stay native.
  viewport.addEventListener('wheel', event => {
    if (!event.ctrlKey) return;
    event.preventDefault();
    if (safariGesture) return;
    const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? viewport.clientHeight : 1);
    setZoom(zoom * Math.exp(-delta * .009), event.clientX, event.clientY);
  }, {passive: false});
  // Safari exposes trackpad gestures separately. Avoid processing both streams.
  viewport.addEventListener('gesturestart', event => {
    event.preventDefault();
    safariGesture = {zoom};
  }, {passive: false});
  viewport.addEventListener('gesturechange', event => {
    event.preventDefault();
    if (safariGesture && !touchGesture) setZoom(safariGesture.zoom * event.scale, event.clientX, event.clientY);
  }, {passive: false});
  viewport.addEventListener('gestureend', event => { event.preventDefault(); safariGesture = null; }, {passive: false});

  // Two-touch fallback. One-finger scrolling remains native.
  const touchPoint = touches => ({
    distance: Math.hypot(touches[0].clientX - touches[1].clientX, touches[0].clientY - touches[1].clientY),
    x: (touches[0].clientX + touches[1].clientX) / 2,
    y: (touches[0].clientY + touches[1].clientY) / 2
  });
  viewport.addEventListener('touchstart', event => {
    if (event.touches.length !== 2) return;
    event.preventDefault();
    const point = touchPoint(event.touches);
    touchGesture = {zoom, ...point};
  }, {passive: false});
  viewport.addEventListener('touchmove', event => {
    if (!touchGesture || event.touches.length !== 2) return;
    event.preventDefault();
    const point = touchPoint(event.touches);
    if (touchGesture.distance > 0) setZoom(touchGesture.zoom * point.distance / touchGesture.distance, point.x, point.y);
  }, {passive: false});
  const endTouch = event => { if (event.touches.length < 2) touchGesture = null; };
  viewport.addEventListener('touchend', endTouch, {passive: true});
  viewport.addEventListener('touchcancel', () => { touchGesture = null; safariGesture = null; }, {passive: true});

  function stopDrag() {
    if (dragging && viewport.hasPointerCapture(dragging.pointerId)) viewport.releasePointerCapture(dragging.pointerId);
    dragging = null;
    viewport.classList.remove('grabbing');
  }
  function releasePan() { spaceHeld = false; viewport.classList.remove('pannable'); stopDrag(); }
  const interactiveTarget = target => target instanceof Element && target.closest('button, a, input, textarea, select, [contenteditable="true"], dialog');
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && settings.open && !help.open) { event.preventDefault(); closeSettings(); return; }
    if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing || help.open || settings.open || interactiveTarget(event.target)) return;
    if (event.code === 'Space') {
      event.preventDefault();
      spaceHeld = true;
      viewport.classList.add('pannable');
    } else if (event.key === '+' || event.key === '=') { event.preventDefault(); setZoom(zoom * 1.18); }
    else if (event.key === '-') { event.preventDefault(); setZoom(zoom / 1.18); }
    else if (event.key === '0') { event.preventDefault(); setZoom(1); }
    else if (event.key === ']') { event.preventDefault(); goTo(active + 1); }
    else if (event.key === '[') { event.preventDefault(); goTo(active - 1); }
  });
  document.addEventListener('keyup', event => { if (event.code === 'Space') releasePan(); });
  window.addEventListener('blur', releasePan);
  viewport.addEventListener('pointerdown', event => {
    if (!spaceHeld || event.button !== 0 || interactiveTarget(event.target)) return;
    event.preventDefault();
    dragging = {pointerId: event.pointerId, x: event.clientX, y: event.clientY, left: viewport.scrollLeft, top: viewport.scrollTop};
    viewport.classList.add('grabbing');
    viewport.setPointerCapture(event.pointerId);
  });
  viewport.addEventListener('pointermove', event => {
    if (!dragging || dragging.pointerId !== event.pointerId) return;
    viewport.scrollLeft = dragging.left - (event.clientX - dragging.x);
    viewport.scrollTop = dragging.top - (event.clientY - dragging.y);
  });
  viewport.addEventListener('pointerup', stopDrag);
  viewport.addEventListener('pointercancel', releasePan);
  viewport.addEventListener('lostpointercapture', stopDrag);

  document.getElementById('open-help').addEventListener('click', () => { releasePan(); help.showModal(); });
  document.getElementById('close-help').addEventListener('click', () => help.close());
  help.addEventListener('click', event => {
    const rect = help.getBoundingClientRect();
    if (event.target === help && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) help.close();
  });
  window.addEventListener('popstate', () => {
    const index = hashIndex();
    if (index >= 0) goTo(index, 'none');
    else { viewport.scrollTop = 0; updateNavigation(0); }
  });
  window.addEventListener('hashchange', () => { const index = hashIndex(); if (index >= 0) goTo(index, 'none'); });
  window.addEventListener('resize', () => { updateTail(); if (fitMode) fitSheet(); scheduleNavigation(); });
  window.addEventListener('pagehide', savePosition);
  document.querySelectorAll('a[href="contents.html"], a[href="notes.html"]').forEach(link => link.addEventListener('click', savePosition));
  const saved = readPosition();
  const initialHash = hashIndex();
  applyLanguages(false);
  updateTail();
  // Wait through the browser's initial anchor positioning before restoring the sheet.
  const restoreReadingPosition = () => requestAnimationFrame(() => requestAnimationFrame(() => {
    if (Number.isFinite(saved.zoom)) setZoom(saved.zoom, 0, viewport.getBoundingClientRect().top);
    viewport.scrollLeft = Number.isFinite(saved.left) ? saved.left : 0;
    if (location.hash === `#${sheet.dataset.chapterAnchor}`) { viewport.scrollTop = 0; viewport.scrollLeft = 0; }
    else if (initialHash >= 0) goTo(initialHash, 'none');
    else if (Number.isFinite(saved.top)) viewport.scrollTop = saved.top;
    syncNavigation();
  }));
  if (document.fonts) document.fonts.ready.then(restoreReadingPosition);
  else restoreReadingPosition();
})();

