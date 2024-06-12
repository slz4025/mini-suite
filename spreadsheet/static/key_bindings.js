function inputting() {
    const activeEle = document.activeElement;
    const nodeType = activeEle.nodeName;
    return ["INPUT", "TEXTAREA"].includes(nodeType);
}

window.addEventListener('keydown', async function(event) {
  // We don't put these key-bindings under a Ctrl or Meta because browsers
  // often use Ctrl Meta key-bindings already.
  if (!event.ctrlKey && !event.metaKey) {
    switch (event.key) {
      case 'Escape':
        const activeEle = document.activeElement;
        activeEle?.blur();
        break;
    }

    // Only allow the following keys if the user is not in an input.
    // The following keys in an input by default are used in the input.
    if (!inputting()) {
      switch (event.key) {
        // modes
        case '0':
          document.getElementById("command-palette-toggler").click();
          break;
        case '1':
          document.getElementById("help-toggler").click();
          break;
        case '2':
          document.getElementById("selector-toggler").click();
          break;
        case '3':
          document.getElementById("editor-toggler").click();
          break;
        case '4':
          document.getElementById("bulk-editor-toggler").click();
          break;
        case '5':
          document.getElementById("navigator-toggler").click();
          break;

        // save
        case 's':
          document.getElementById("save-button").click();
          break;

        // selector
        case 'f':
          if (document.getElementById("command-palette").style.display == 'none') {
            await htmx.ajax('PUT', `/command-palette/toggle`, {
              target: `body`,
              swap: "outerHTML",
            });
          }
          if (document.getElementById("selector").style.display == 'none') {
            await htmx.ajax('PUT', `/selector/toggle`, {
              target: `#selector`,
              swap: "outerHTML",
            });
          }
          await htmx.ajax('GET', `/selector/input`, {
            target: `#selector`,
            swap: "outerHTML",
            values: {"mode": "Cell Position"},
          });
          // attempt to focus on searchbar if possible
          document.getElementById("selector-text-search")?.focus();
        case 'q':
          document.getElementById("clear-selector-button")?.click();
          break;

        // bulk editor
        case 'x':
          htmx.ajax('POST', `/bulk-editor/apply/Cut`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;
        case 'c':
          htmx.ajax('POST', `/bulk-editor/apply/Copy`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;
        case 'v':
          htmx.ajax('POST', `/bulk-editor/apply/Paste`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;
        case 'm':
          htmx.ajax('POST', `/bulk-editor/apply/Move Forward`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;
        case 'n':
          htmx.ajax('POST', `/bulk-editor/apply/Move Backward`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;
        case 'i':
          htmx.ajax('POST', `/bulk-editor/apply/Insert`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;
        case 'l':
          htmx.ajax('POST', `/bulk-editor/apply/Insert End Rows`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;
        case 'L':
          htmx.ajax('POST', `/bulk-editor/apply/Insert End Columns`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;
        // On a Mac, this is done via Fn+Backspace (which might say "delete").
        case 'Delete':
          htmx.ajax('POST', `/bulk-editor/apply/Delete`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;

        // viewer
        case 'h':
          document.getElementById("home-button").click();
          break;
        case 't':
          document.getElementById("viewer-target-button").click();
          break;
        case 'ArrowUp':
          document.getElementById("up-button").click();
          break;
        case 'ArrowDown':
          document.getElementById("down-button").click();
          break;
        case 'ArrowLeft':
          document.getElementById("left-button").click();
          break;
        case 'ArrowRight':
          document.getElementById("right-button").click();
          break;
      }
    }
  }
});
