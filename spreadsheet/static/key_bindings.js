window.addEventListener('keydown', function(event) {
  if (event.ctrlKey) {
    switch (event.key) {
      // modes
      case '0':
        document.getElementById("help-toggler").click();
        break;
      case '1':
        document.getElementById("selector-toggler").click();
        break;
      case '2':
        document.getElementById("editor-toggler").click();
        break;
      case '3':
        document.getElementById("bulk-editor-toggler").click();
        break;
      case '4':
        document.getElementById("navigator-toggler").click();
        break;

      // save
      case 's':
        document.getElementById("files-save").click();
        break;

      // selector
      case 'q':
        document.getElementById("clear-selector-button")?.click();
        break;

      // bulk edit
      case 'x':
        if (!editing()) {
          htmx.ajax('POST', `/bulk-editor/apply/Cut`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
        }
        break;
      case 'c':
        if (!editing()) {
          htmx.ajax('POST', `/bulk-editor/apply/Copy`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
        }
        break;
      case 'v':
        if (!editing()) {
          htmx.ajax('POST', `/bulk-editor/apply/Paste`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
        }
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
        if (!editing()) {
          htmx.ajax('POST', `/bulk-editor/apply/Delete`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
        }
        break;

      // view
      case 'h':
        document.getElementById("home-button").click();
        break;
      case 't':
        document.getElementById("viewer-target-button").click();
        break;
    }
  } else {
    switch (event.key) {
      // move around port
      case 'ArrowUp':
        if (!editing()) {
          document.getElementById("up-button").click();
        }
        break;
      case 'ArrowDown':
        if (!editing()) {
          document.getElementById("down-button").click();
        }
        break;
      case 'ArrowLeft':
        if (!editing()) {
          document.getElementById("left-button").click();
        }
        break;
      case 'ArrowRight':
        if (!editing()) {
          document.getElementById("right-button").click();
        }
        break;
    }
  }
});
