(() => {
  // Header: stato "scrolled" per ombra e sfondo pieno
  const header = document.querySelector('.site-header');
  if (header) {
    const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Filtro testuale per le liste (episodi, geek)
  const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

  document.querySelectorAll('[data-filter-input]').forEach(input => {
    const scope = document.querySelector(input.dataset.filterInput);
    if (!scope) return;
    const items = [...scope.querySelectorAll('[data-filter-item]')];
    const groups = [...scope.querySelectorAll('[data-filter-group]')];
    const counter = input.dataset.filterCount && document.querySelector(input.dataset.filterCount);
    const empty = scope.querySelector('[data-filter-empty]');
    const texts = new Map(items.map(i => [i, norm(i.textContent)]));

    const run = () => {
      const terms = norm(input.value).split(/\s+/).filter(Boolean);
      let shown = 0;
      items.forEach(i => {
        const ok = terms.every(t => texts.get(i).includes(t));
        i.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach(g => { g.hidden = !g.querySelector('[data-filter-item]:not([hidden])'); });
      if (counter) counter.textContent = shown;
      if (empty) empty.hidden = shown > 0;
    };

    input.addEventListener('input', run);

    // "/" porta il focus sulla ricerca, Esc la svuota
    document.addEventListener('keydown', e => {
      if (e.key === '/' && document.activeElement !== input && !/input|textarea/i.test(document.activeElement.tagName)) {
        e.preventDefault();
        input.focus();
      } else if (e.key === 'Escape' && document.activeElement === input) {
        input.value = '';
        run();
      }
    });
  });
})();
