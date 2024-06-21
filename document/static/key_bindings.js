function inputting() {
    const activeEle = document.activeElement;
    const nodeType = activeEle.nodeName;
    return ["INPUT", "TEXTAREA"].includes(nodeType);
}

window.addEventListener('keyup', async function(event) {
  if (event.shiftKey) {
    switch (event.key) {
      case 'ArrowUp':
        document.getElementById("prev-block-button")?.click();
        break;
      case 'ArrowDown':
        document.getElementById("next-block-button")?.click();
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
        document.getElementById("render-block-button")?.click();
        break;
    }
  }
});
