/* Rosettapada: native scrolling, selectable text, and one continuously scaled sheet. */
(() => {
  'use strict';
  const viewport = document.getElementById('viewport');
  if (!viewport) return;
  const sheet = document.getElementById('sheet');
  const headings = document.getElementById('column-headings');
  const verses = Array.from(sheet.querySelectorAll('.verse'));
  const prev = document.getElementById('prev');
  const next = document.getElementById('next');
  const label = document.getElementById('location');
  const zoomLabel = document.getElementById('zoom-label');
  const announcement = document.getElementById('zoom-announcement');
  const help = document.getElementById('reading-help');
  const minZoom = .1;
  const maxZoom = 3;
  const storageKey = 'rosettapada-reading-v3';
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
    const text = `Verse ${verses[active].dataset.verse} of ${verses.length}`;
    if (label.textContent !== text) label.textContent = text;
    prev.disabled = active === 0;
    next.disabled = active === verses.length - 1;
  }
  function readingTop() {
    return viewport.getBoundingClientRect().top + headings.getBoundingClientRect().height + 28 * zoom;
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
  function setZoom(factor, clientX, clientY) {
    if (!Number.isFinite(factor)) return;
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
  prev.addEventListener('click', () => goTo(active - 1));
  next.addEventListener('click', () => goTo(active + 1));
  document.getElementById('zoom-out').addEventListener('click', () => setZoom(zoom / 1.18));
  document.getElementById('zoom-in').addEventListener('click', () => setZoom(zoom * 1.18));
  document.getElementById('reset-zoom').addEventListener('click', () => setZoom(1));
  document.getElementById('fit-sheet').addEventListener('click', () => {
    setZoom(Math.min(1, viewport.clientWidth / sheet.offsetWidth));
  });
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
    if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing || help.open || interactiveTarget(event.target)) return;
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
  window.addEventListener('resize', () => { updateTail(); scheduleNavigation(); });
  window.addEventListener('pagehide', savePosition);
  document.querySelectorAll('a[href="contents.html"], a[href="notes.html"]').forEach(link => link.addEventListener('click', savePosition));
  const saved = readPosition();
  const initialHash = hashIndex();
  updateTail();
  // Wait through the browser's initial anchor positioning before restoring the sheet.
  requestAnimationFrame(() => requestAnimationFrame(() => {
    if (Number.isFinite(saved.zoom)) setZoom(saved.zoom, 0, viewport.getBoundingClientRect().top);
    viewport.scrollLeft = Number.isFinite(saved.left) ? saved.left : 0;
    if (initialHash >= 0) goTo(initialHash, 'none');
    else if (Number.isFinite(saved.top)) viewport.scrollTop = saved.top;
    syncNavigation();
  }));
})();

