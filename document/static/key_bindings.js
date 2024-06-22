function inputting() {
    const activeEle = document.activeElement;
    const nodeType = activeEle.nodeName;
    return ["INPUT", "TEXTAREA"].includes(nodeType);
}

window.addEventListener('keyup', function(event) {
  switch (event.key) {
    case 's':
      if (!inputting()) {
        document.getElementById("save").click();
      }
      break;
    case 'Escape':
      event.preventDefault();
      document.getElementById("render-block-button")?.click();
      break;
    case 'PageUp':
      event.preventDefault(); // don't scroll in textarea
      document.getElementById("prev-block-button")?.click();
      break;
    case 'PageDown':
      event.preventDefault(); // don't scroll in textarea
      document.getElementById("next-block-button")?.click();
      break;
    case 'Insert':
      event.preventDefault();
      document.getElementById("insert-block-button")?.click();
      break;
    case 'Delete':
      event.preventDefault();
      document.getElementById("delete-block-button")?.click();
      break;
  }
});
