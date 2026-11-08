/* Rosettapada: native scrolling, selectable text, and one continuously scaled sheet. */
(() => {
  'use strict';
  const viewport = document.getElementById('viewport');
  if (!viewport) return;
  const sheet = document.getElementById('sheet');
  const headings = document.getElementById('column-headings');
  const verses = Array.from(sheet.querySelectorAll('.verse'));
  const chapterNavigation = sheet.querySelector('.chapter-navigation');
  const label = document.getElementById('location');
  const announcement = document.getElementById('zoom-announcement');
  const zoomToast = document.getElementById('zoom-toast');
  const help = document.getElementById('reading-help');
  const helpButton = document.getElementById('open-help');
  const settingsAnnouncement = document.getElementById('settings-announcement');
  const englishSelect = document.getElementById('english-source');
  const englishStatus = document.getElementById('english-source-status');
  const englishEditions = englishSelect ? JSON.parse(document.getElementById('english-editions').textContent) : {};
  const columnHeads = Array.from(headings.children);
  const defaultOrder = columnHeads.map(column => column.dataset.language);
  const columnByKey = new Map(columnHeads.map(column => [column.dataset.language, column]));
  const groups = [headings, ...document.querySelectorAll('.verse-grid')];
  const groupColumns = groups.map(group => new Map(Array.from(group.children).map(column => [column.dataset.language, column])));
  const englishPoems = englishSelect ? verses.map(verse => {
    const column = verse.querySelector('.lang-en');
    const poem = column.querySelector('.poem');
    return {column, poem, pali: Array.from(poem.childNodes), label: column.querySelector('h3'), number: verse.dataset.verse};
  }) : [];
  const minZoom = .1;
  const maxZoom = 3;
  const isChapter = sheet.dataset.profile !== 'sample';
  const storageKey = isChapter ? `rosettapada-reading-v5-${sheet.dataset.pageKey}` : 'rosettapada-reading-v4';
  const languageStorageKey = isChapter ? 'rosettapada-languages-historical-v1' : 'rosettapada-languages-v1';
  const previousPage = sheet.dataset.previousPage;
  const nextPage = sheet.dataset.nextPage;
  const clamp = (n, min, max) => Math.min(max, Math.max(min, n));
  const nameOf = key => columnByKey.get(key).dataset.label;
  let zoom = 1;
  let active = 0;
  let spaceHeld = false;
  let dragging = null;
  let safariGesture = null;
  let touchGesture = null;
  let frame = 0;
  let saveTimer;
  let announcementTimer;
  let toastTimer;
  let fitMode = false;
  let languageOrder = defaultOrder.slice();
  let hiddenLanguages = new Set(defaultOrder.filter(key => key === 'zh-pinyin'));
  let columnDrag = null;
  let englishPreference = 'pi';
  let displayedEnglish = 'pi';

  // Elements that live in the heading row but outside its grid: the drop marker and the shelf of hidden columns.
  const dropMarker = document.createElement('div');
  dropMarker.className = 'column-drop-marker';
  dropMarker.hidden = true;
  const shelf = document.createElement('div');
  shelf.className = 'column-shelf';
  shelf.setAttribute('role', 'group');
  shelf.setAttribute('aria-label', 'Hidden columns');
  headings.append(dropMarker, shelf);

  try {
    const saved = JSON.parse(localStorage.getItem(languageStorageKey));
    if (saved && Array.isArray(saved.order)) languageOrder = Array.from(new Set([...saved.order.filter(key => defaultOrder.includes(key)), ...defaultOrder]));
    if (saved && Array.isArray(saved.hidden)) hiddenLanguages = new Set(saved.hidden.filter(key => defaultOrder.includes(key)));
    if (englishSelect && Array.from(englishSelect.options).some(option => option.value === saved?.english)) englishPreference = saved.english;
    if (hiddenLanguages.size === defaultOrder.length) hiddenLanguages.delete('en');
  } catch { /* Defaults work when storage is unavailable or its contents are invalid. */ }

  function saveLanguages() {
    try { localStorage.setItem(languageStorageKey, JSON.stringify({order: languageOrder, hidden: Array.from(hiddenLanguages), english: englishPreference})); }
    catch { /* Settings still apply for this visit. */ }
  }
  function orderChildren(parent, elements) {
    languageOrder.forEach((key, index) => {
      const element = elements.get(key);
      if (parent.children[index] !== element) parent.insertBefore(element, parent.children[index] || null);
    });
  }
  // Browsers size a select to its longest option; fit it to the chosen label so the chevron follows the text.
  // A hidden span in the same label measures with exactly the font the page renders.
  function fitEnglishSelect() {
    const style = getComputedStyle(englishSelect);
    let probe = englishSelect.parentElement.querySelector('.english-source-measure');
    if (!probe) {
      probe = document.createElement('span');
      probe.className = 'english-source-measure';
      probe.setAttribute('aria-hidden', 'true');
      Object.assign(probe.style, {position: 'absolute', visibility: 'hidden', whiteSpace: 'pre', left: '0', top: '0'});
      englishSelect.parentElement.append(probe);
    }
    probe.style.font = style.font;
    probe.style.letterSpacing = style.letterSpacing;
    probe.textContent = englishSelect.selectedOptions[0]?.textContent || '';
    englishSelect.style.width = `${Math.ceil(probe.offsetWidth + parseFloat(style.paddingLeft) + parseFloat(style.paddingRight) + 2)}px`;
  }
  function applyEnglish() {
    if (!englishSelect) return;
    const preferred = Array.from(englishSelect.options).find(option => option.value === englishPreference);
    const available = preferred && !preferred.disabled;
    const source = available ? englishPreference : 'pi';
    const name = preferred?.dataset.label || 'Pāli';
    // Show the source actually on the sheet; a saved preference returns where a translation exists.
    englishSelect.value = source;
    englishStatus.textContent = !available
      ? `Using Pāli here. ${name} will return where available.`
      : source !== 'pi' ? 'A dash marks a verse this tradition does not have.' : '';
    englishSelect.title = available ? 'Choose the English translation source' : `${name} has no translation in this chapter; showing the Pāli-based English`;
    fitEnglishSelect();
    if (source === displayedEnglish) return;
    displayedEnglish = source;
    englishPoems.forEach(({column, poem, pali, label, number}) => {
      const lines = englishEditions[source]?.[number];
      const missing = source !== 'pi' && !lines;
      column.dataset.readingStatus = missing ? 'unverified' : 'present';
      label.textContent = source === 'pi' ? `English, verse ${number}` : `English from ${name}, verse ${number}${missing ? ', no parallel' : ''}`;
      if (source === 'pi') poem.replaceChildren(...pali);
      else if (missing) poem.textContent = '—';
      else poem.replaceChildren(...lines.map(text => {
        const line = document.createElement('span');
        line.className = 'poem-line';
        line.textContent = text;
        return line;
      }));
    });
  }
  function renderShelf() {
    const hidden = languageOrder.filter(key => hiddenLanguages.has(key));
    shelf.replaceChildren(...hidden.map(key => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'column-show';
      button.dataset.language = key;
      button.title = `Show ${nameOf(key)}`;
      button.setAttribute('aria-label', `Show ${nameOf(key)}`);
      button.innerHTML = '<span aria-hidden="true">+</span>';
      button.append(nameOf(key));
      return button;
    }));
    shelf.hidden = !hidden.length;
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
    columnByKey.forEach((head, key) => {
      const button = head.querySelector('.column-hide');
      button.disabled = visible.length === 1 && !hiddenLanguages.has(key);
      button.title = button.disabled ? 'Keep at least one column visible' : 'Hide this column';
    });
    renderShelf();
    applyEnglish();
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
    // Step past hidden columns so each key press visibly moves the column; hidden ones keep their places.
    const from = languageOrder.indexOf(key);
    let j = from + delta;
    while (j >= 0 && j < languageOrder.length && hiddenLanguages.has(languageOrder[j])) j += delta;
    if (from < 0 || j < 0 || j >= languageOrder.length) return;
    const neighbour = languageOrder[j];
    languageOrder.splice(from, 1);
    languageOrder.splice(languageOrder.indexOf(neighbour) + (delta > 0 ? 1 : 0), 0, key);
    applyLanguages();
    columnByKey.get(key).focus({preventScroll: true});
    const position = languageOrder.filter(k => !hiddenLanguages.has(k)).indexOf(key) + 1;
    settingsAnnouncement.textContent = `${nameOf(key)} moved to position ${position}`;
  }

  // Column headings are the drag handles. A mouse drags immediately; a touch must press and hold first,
  // so ordinary swiping on the heading row still scrolls the sheet.
  const isControl = target => target.closest('select, button, label.english-source');
  function visibleHeads() { return languageOrder.filter(key => !hiddenLanguages.has(key)).map(key => columnByKey.get(key)); }
  function dropTarget(clientX) {
    const heads = visibleHeads().filter(head => head.dataset.language !== columnDrag.key);
    const before = heads.find(head => { const rect = head.getBoundingClientRect(); return clientX < rect.left + rect.width / 2; });
    return before || null;
  }
  function showDropMarker(before) {
    const heads = visibleHeads();
    const box = headings.getBoundingClientRect();
    const gutter = parseFloat(getComputedStyle(headings).columnGap) * zoom;
    let x;
    if (before) x = before.getBoundingClientRect().left - gutter / 2;
    else x = heads.filter(head => head.dataset.language !== columnDrag.key).at(-1).getBoundingClientRect().right + gutter / 2;
    dropMarker.style.left = `${(x - box.left) / zoom}px`;
    dropMarker.hidden = false;
  }
  function startColumnDrag() {
    columnDrag.started = true;
    const head = columnByKey.get(columnDrag.key);
    head.classList.add('is-lifted');
    headings.classList.add('is-reordering');
    window.getSelection()?.removeAllRanges();
  }
  function edgeScroll() {
    if (!columnDrag?.started) return;
    const rect = viewport.getBoundingClientRect();
    const edge = 70;
    const x = columnDrag.lastX;
    const speed = x < rect.left + edge ? -(rect.left + edge - x) / 3 : x > rect.right - edge ? (x - (rect.right - edge)) / 3 : 0;
    if (speed) {
      viewport.scrollLeft += speed;
      trackColumnDrag(columnDrag.lastX);
    }
    columnDrag.edgeFrame = requestAnimationFrame(edgeScroll);
  }
  function trackColumnDrag(clientX) {
    const head = columnByKey.get(columnDrag.key);
    const shift = (clientX - columnDrag.x + (viewport.scrollLeft - columnDrag.scrollLeft)) / zoom;
    head.style.transform = `translateX(${shift}px)`;
    const before = dropTarget(clientX);
    columnDrag.before = before?.dataset.language || null;
    showDropMarker(before);
  }
  function endColumnDrag(commit) {
    if (!columnDrag) return;
    const drag = columnDrag;
    columnDrag = null;
    clearTimeout(drag.holdTimer);
    cancelAnimationFrame(drag.edgeFrame);
    const head = columnByKey.get(drag.key);
    head.classList.remove('is-lifted', 'is-pressed');
    head.style.transform = '';
    headings.classList.remove('is-reordering');
    dropMarker.hidden = true;
    if (headings.hasPointerCapture?.(drag.pointerId)) headings.releasePointerCapture(drag.pointerId);
    if (!commit || !drag.started) return;
    languageOrder = languageOrder.filter(key => key !== drag.key);
    const index = drag.before === null ? languageOrder.length : languageOrder.indexOf(drag.before);
    languageOrder.splice(index, 0, drag.key);
    applyLanguages();
    settingsAnnouncement.textContent = `${nameOf(drag.key)} moved`;
  }
  headings.addEventListener('pointerdown', event => {
    const head = event.target.closest('.column-heading');
    if (!head || isControl(event.target) || event.button !== 0 || spaceHeld) return;
    const touch = event.pointerType === 'touch';
    columnDrag = {key: head.dataset.language, pointerId: event.pointerId, x: event.clientX, y: event.clientY, lastX: event.clientX,
      scrollLeft: viewport.scrollLeft, started: false, touch, armed: !touch, before: null, holdTimer: 0, edgeFrame: 0};
    if (touch) {
      columnDrag.holdTimer = setTimeout(() => {
        if (!columnDrag) return;
        columnDrag.armed = true;
        head.classList.add('is-pressed');
        navigator.vibrate?.(8);
      }, 320);
      return;
    }
    event.preventDefault();
    head.focus({preventScroll: true});
    headings.setPointerCapture(event.pointerId);
  });
  headings.addEventListener('pointermove', event => {
    if (!columnDrag || columnDrag.pointerId !== event.pointerId) return;
    const distance = Math.hypot(event.clientX - columnDrag.x, event.clientY - columnDrag.y);
    if (!columnDrag.armed) {
      if (distance > 8) endColumnDrag(false);
      return;
    }
    columnDrag.lastX = event.clientX;
    if (!columnDrag.started) {
      if (distance < 4) return;
      startColumnDrag();
      columnDrag.edgeFrame = requestAnimationFrame(edgeScroll);
    }
    trackColumnDrag(event.clientX);
  });
  headings.addEventListener('pointerup', event => { if (columnDrag?.pointerId === event.pointerId) endColumnDrag(true); });
  headings.addEventListener('pointercancel', () => endColumnDrag(false));
  // Once a touch press is armed, stop the browser from turning the movement into a scroll.
  headings.addEventListener('touchmove', event => { if (columnDrag?.armed) event.preventDefault(); }, {passive: false});
  headings.addEventListener('contextmenu', event => { if (columnDrag?.touch) event.preventDefault(); });
  headings.addEventListener('keydown', event => {
    const head = event.target.closest('.column-heading');
    if (!head || event.target !== head || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    moveLanguage(head.dataset.language, event.key === 'ArrowLeft' ? -1 : 1);
  });
  headings.addEventListener('click', event => {
    const hide = event.target.closest('.column-hide');
    const show = event.target.closest('.column-show');
    if (hide && !hide.disabled) {
      hiddenLanguages.add(hide.dataset.language);
      applyLanguages();
      settingsAnnouncement.textContent = `${nameOf(hide.dataset.language)} hidden`;
      (shelf.querySelector(`[data-language="${hide.dataset.language}"]`) || viewport).focus({preventScroll: true});
    } else if (show) {
      hiddenLanguages.delete(show.dataset.language);
      applyLanguages();
      settingsAnnouncement.textContent = `${nameOf(show.dataset.language)} shown`;
      columnByKey.get(show.dataset.language).focus({preventScroll: true});
    }
  });
  englishSelect?.addEventListener('change', () => {
    englishPreference = englishSelect.value;
    hiddenLanguages.delete('en');
    applyLanguages();
  });
  document.getElementById('restore-languages').addEventListener('click', () => {
    languageOrder = defaultOrder.slice();
    hiddenLanguages = new Set(defaultOrder.filter(key => key === 'zh-pinyin'));
    englishPreference = 'pi';
    applyLanguages();
    settingsAnnouncement.textContent = 'Default layout restored';
    help.close();
  });
  helpButton.addEventListener('click', () => {
    releasePan();
    help.showModal();
    helpButton.setAttribute('aria-expanded', 'true');
  });
  document.getElementById('close-help').addEventListener('click', () => help.close());
  help.addEventListener('close', () => {
    helpButton.setAttribute('aria-expanded', 'false');
    helpButton.focus({preventScroll: true});
  });
  help.addEventListener('click', event => {
    const rect = help.getBoundingClientRect();
    if (event.target === help && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) help.close();
  });

  function readPosition() {
    try { return JSON.parse(sessionStorage.getItem(storageKey)) || {}; }
    catch { return {}; }
  }
  function savePosition() {
    try {
      sessionStorage.setItem(storageKey, JSON.stringify({zoom, left: viewport.scrollLeft, top: viewport.scrollTop, verse: active}));
      // Contents and Notes offer a way back to this chapter, shown at the same magnification.
      localStorage.setItem('rosettapada-last-reading', JSON.stringify({page: `${sheet.dataset.pageKey}.html`, title: sheet.dataset.chapterTitle || 'the sample', zoom}));
    } catch { /* Reading still works when browser storage is unavailable. */ }
  }
  function scheduleSave() { clearTimeout(saveTimer); saveTimer = setTimeout(savePosition, 160); }
  function updateTail() {
    if (!chapterNavigation) {
      sheet.style.paddingBottom = `${Math.max(160, viewport.clientHeight / zoom - 220)}px`;
      return;
    }
    // Make room to bring the last verse to the reading line, with the links at the end.
    const beforeLinks = chapterNavigation.getBoundingClientRect().top - verses.at(-1).getBoundingClientRect().top;
    const linksHeight = chapterNavigation.firstElementChild.getBoundingClientRect().height;
    const bottom = parseFloat(getComputedStyle(sheet).paddingBottom) * zoom;
    const spare = viewport.clientHeight - headings.getBoundingClientRect().height - 16 * zoom - beforeLinks - linksHeight - bottom;
    chapterNavigation.style.paddingTop = `${Math.max(0, spare / zoom)}px`;
  }
  function announceZoom() {
    clearTimeout(announcementTimer);
    announcementTimer = setTimeout(() => { announcement.textContent = `Sheet magnification ${Math.round(zoom * 100)} percent`; }, 180);
  }
  function showZoom() {
    zoomToast.textContent = fitMode ? `Fit · ${Math.round(zoom * 100)}%` : `${Math.round(zoom * 100)}%`;
    zoomToast.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => zoomToast.classList.remove('is-visible'), 900);
  }
  function updateNavigation(index) {
    active = clamp(index, 0, verses.length - 1);
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
    const target = clamp(factor, minZoom, maxZoom);
    if (Math.abs(target - zoom) < .0001) { if (mode !== 'restore') showZoom(); return; }
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
    if (mode !== 'restore') showZoom();
    scheduleNavigation();
    announceZoom();
    scheduleSave();
  }
  function turnChapter(adjacentPage) {
    savePosition();
    const pageKey = adjacentPage.split('#')[0].replace(/\.html$/, '');
    try {
      sessionStorage.setItem(`rosettapada-reading-v5-${pageKey}`, JSON.stringify({zoom, left: viewport.scrollLeft, top: 0}));
    } catch { /* The chapter link still works when browser storage is unavailable. */ }
    location.assign(adjacentPage);
  }
  function goTo(index, historyMode = 'push') {
    const adjacentPage = index < 0 ? previousPage : index >= verses.length ? nextPage : '';
    if (adjacentPage) return turnChapter(adjacentPage);
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
  chapterNavigation?.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    turnChapter(link.getAttribute('href'));
  });
  function fitSheet() { setZoom(Math.min(1, viewport.clientWidth / sheet.offsetWidth), undefined, undefined, 'fit'); }
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
    endColumnDrag(false);
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
    if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing || help.open || interactiveTarget(event.target)) return;
    if (event.key === 'Escape' && columnDrag) { endColumnDrag(false); return; }
    if (event.code === 'Space') {
      event.preventDefault();
      spaceHeld = true;
      viewport.classList.add('pannable');
    } else if (event.key === '+' || event.key === '=') { event.preventDefault(); setZoom(zoom * 1.18); }
    else if (event.key === '-') { event.preventDefault(); setZoom(zoom / 1.18); }
    else if (event.key === '0') { event.preventDefault(); setZoom(1); }
    else if (event.key === 'f' || event.key === 'F') { event.preventDefault(); fitSheet(); }
    else if (event.key === ']') { event.preventDefault(); goTo(active + 1); }
    else if (event.key === '[') { event.preventDefault(); goTo(active - 1); }
  });
  document.addEventListener('keyup', event => { if (event.code === 'Space') releasePan(); });
  window.addEventListener('blur', () => { releasePan(); endColumnDrag(false); });
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
  // Wait through the browser's initial anchor positioning before restoring the sheet.
  const restoreReadingPosition = () => requestAnimationFrame(() => requestAnimationFrame(() => {
    if (Number.isFinite(saved.zoom)) setZoom(saved.zoom, 0, viewport.getBoundingClientRect().top, 'restore');
    updateTail();
    viewport.scrollLeft = Number.isFinite(saved.left) ? saved.left : 0;
    if (location.hash === `#${sheet.dataset.chapterAnchor}`) { viewport.scrollTop = 0; viewport.scrollLeft = 0; }
    else if (initialHash >= 0) goTo(initialHash, 'none');
    else if (Number.isFinite(saved.top)) viewport.scrollTop = saved.top;
    syncNavigation();
    savePosition();
  }));
  if (document.fonts) document.fonts.ready.then(restoreReadingPosition);
  else restoreReadingPosition();
})();
