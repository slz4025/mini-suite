function inputting() {
    const activeEle = document.activeElement;
    const nodeType = activeEle.nodeName;
    return ["INPUT", "TEXTAREA"].includes(nodeType);
}

window.addEventListener('keyup', async function(event) {
  const resp = await fetch("/block/infocus");
  const json = await resp.json();
  const id = json.id;

  if (event.shiftKey) {
    switch (event.key) {
      case 'ArrowUp':
        if (id !== undefined) {
          htmx.ajax('POST', `/block/prev`, {
            target: `#block-${id}`,
            swap: "outerHTML",
          });
        }
        break;
      case 'ArrowDown':
        if (id !== undefined) {
          htmx.ajax('POST', `/block/next`, {
            target: `#block-${id}`,
            swap: "outerHTML",
          });
        }
        break;
    }
  } else {
    switch (event.key) {
      case 's':
        if (!inputting()) {
          document.getElementById("save").click();
        }
        break;
      case 'Escape':
        if (id !== undefined) {
          htmx.ajax('POST', `/block/unfocus`, {
            target: `#block-${id}`,
            swap: "outerHTML",
          });
        }
        break;
    }
  }
});
