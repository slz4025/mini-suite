window.addEventListener('keydown', function(event) {
  if (event.ctrlKey) {
    switch (event.key) {
      // modes
      case '0':
        document.getElementById("help-toggler").click();
        break;
      case '1':
        document.getElementById("editor-toggler").click();
        break;
      case '2':
        document.getElementById("selection-toggler").click();
        break;
      case '3':
        document.getElementById("bulk-editor-toggler").click();
        break;
      case '4':
        document.getElementById("navigator-toggler").click();
        break;

      // selection
      case 'q':
        document.getElementById("up-selection-button")?.click();
        break;
      case 'w':
        document.getElementById("down-selection-button")?.click();
        break;
      case 'e':
        document.getElementById("left-selection-button")?.click();
        break;
      case 'r':
        document.getElementById("right-selection-button")?.click();
        break;
      case 'y':
        document.getElementById("right-selection-button")?.click();
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

      // view
      case 'h':
        document.getElementById("home-button").click();
        break;
      case 't':
        document.getElementById("navigator-target-button").click();
        break;
      case 'i':
        document.getElementById("up-button").click();
        break;
      case 'k':
        document.getElementById("down-button").click();
        break;
      case 'j':
        document.getElementById("left-button").click();
        break;
      case 'l':
        document.getElementById("right-button").click();
        break;

      // save
      case 's':
        document.getElementById("files-save").click();
        break;
    }
  } else {
    switch (event.key) {
      // On a Mac, this is done via Fn+Backspace (which might say "delete").
      case 'Delete':
        htmx.ajax('POST', `/bulk-editor/apply/Delete`, {
          target: `#bulk-editor`,
          swap: "outerHTML",
        });
        break;
    }
  }
});
