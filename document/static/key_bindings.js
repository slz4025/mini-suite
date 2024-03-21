window.addEventListener('keyup', async function(event) {
  if (event.shiftKey) {
    const resp = await fetch("/block/infocus");
    const json = await resp.json();
    const id = json.id;

    switch (event.key) {
      case 'Enter':
        htmx.ajax('POST', `/block/unfocus`, {
          target: `#block-${id}`,
          swap: "outerHTML",
        });
        break;
      case 'ArrowUp':
        htmx.ajax('POST', `/block/prev`, {
          target: `#block-${id}`,
          swap: "outerHTML",
        });
        break;
      case 'ArrowDown':
        htmx.ajax('POST', `/block/next`, {
          target: `#block-${id}`,
          swap: "outerHTML",
        });
        break;
    }
  }
});
