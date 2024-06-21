function inputting() {
    const activeEle = document.activeElement;
    const nodeType = activeEle.nodeName;
    return ["INPUT", "TEXTAREA"].includes(nodeType);
}

window.addEventListener('keyup', function(event) {
  switch (event.key) {
    /* TODO: Have these also move towards block of interest.
    case 'PageUp':
      document.getElementById("prev-block-button")?.click();
      break;
    case 'PageDown':
      document.getElementById("next-block-button")?.click();
      break;
    */
    case 's':
      if (!inputting()) {
        document.getElementById("save").click();
      }
      break;
    case 'Escape':
      document.getElementById("render-block-button")?.click();
      break;
    case 'Insert':
      document.getElementById("insert-block-button")?.click();
      break;
    case 'Delete':
      document.getElementById("delete-block-button")?.click();
      break;
  }
});
