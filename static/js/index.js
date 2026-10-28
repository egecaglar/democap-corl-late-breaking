'use strict';
for (const card of document.querySelectorAll('[data-comparison]')) {
  const videos = [...card.querySelectorAll('video')];
  const status = card.querySelector('.pair-status');
  let playRequest = 0;
  card.querySelector('.play-pair').addEventListener('click', async () => {
    const request = ++playRequest;
    status.textContent = '';
    videos.forEach(video => { video.pause(); video.currentTime = 0; });
    const results = await Promise.allSettled(videos.map(video => video.play()));
    if (request !== playRequest) return;
    if (results.some(result => result.status === 'rejected')) {
      videos.forEach(video => video.pause());
      status.textContent = 'Playback could not start. Use the individual video controls to retry.';
    }
  });
  card.querySelector('.pair-speed')?.addEventListener('change', event => {
    videos.forEach(video => { video.playbackRate = Number(event.target.value); });
  });
  card.querySelector('.pause-pair').addEventListener('click', () => {
    playRequest++;
    videos.forEach(video => video.pause());
    status.textContent = '';
  });
}

for (const button of document.querySelectorAll('[data-result-filter]')) {
  button.addEventListener('click', () => {
    const condition = button.dataset.resultFilter;
    document.querySelectorAll('[data-result-filter]').forEach(other => {
      other.setAttribute('aria-pressed', String(other === button));
    });
    document.querySelectorAll('[data-result-condition]').forEach(group => {
      group.hidden = condition !== 'all' && group.dataset.resultCondition !== condition;
    });
  });
}

for (const group of document.querySelectorAll('[data-example-group="object-identification"]')) {
  const tabs = [...group.querySelectorAll('[data-identity-tab]')];
  function selectTab(tab, focus = false) {
    group.querySelectorAll('video').forEach(video => video.pause());
    tabs.forEach(other => {
      const selected = other === tab;
      other.setAttribute('aria-selected', String(selected));
      other.tabIndex = selected ? 0 : -1;
    });
    group.querySelectorAll('[data-identity-panel]').forEach(panel => {
      panel.hidden = panel.dataset.identityPanel !== tab.dataset.identityTab;
    });
    if (focus) tab.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectTab(tab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
      if (event.key === 'ArrowLeft') next = tabs[(index - 1 + tabs.length) % tabs.length];
      if (event.key === 'Home') next = tabs[0];
      if (event.key === 'End') next = tabs[tabs.length - 1];
      if (next) { event.preventDefault(); selectTab(next, true); }
    });
  });
}
