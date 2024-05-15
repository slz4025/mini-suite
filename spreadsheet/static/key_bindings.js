window.addEventListener('keyup', function(event) {
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
      case 's':
        document.getElementById("files-save").click();
        break;
      case 't':
        document.getElementById("navigator-target-button").click();
        break;
    }
  } else if (event.shiftKey) {
    switch (event.key) {
      case 'ArrowUp':
        document.getElementById("up-selection-button")?.click();
        break;
      case 'ArrowDown':
        document.getElementById("down-selection-button")?.click();
        break;
      case 'ArrowLeft':
        document.getElementById("left-selection-button")?.click();
        break;
      case 'ArrowRight':
        document.getElementById("right-selection-button")?.click();
        break;
    }
  } else {
    const activeId = document.activeElement.id;
    if (activeId.startsWith("input-cell-")) {
      var arr = activeId.split('-');
      const row = Number(arr[2]);
      const col = Number(arr[3]);

      // The native behavior is that
      // Tab goes right and Shift-Tab goes left.
      // We therefore only encode the desired behavior
      // for Enter (down) and Shift-Enter (up).
      let nextId;
      if (event.shiftKey) {
        switch (event.key) {
          case 'Enter':
            nextId = `input-cell-${row-1}-${col}`;
            break;
        }
      } else {
        switch (event.key) {
          case 'Enter':
            nextId = `input-cell-${row+1}-${col}`;
            break;
        }
      }

      const element = document.getElementById(nextId)
      if (element) {
        element.focus();
      }
    } else {
      switch (event.key) {
        case 'Delete':
          htmx.ajax('POST', `/bulk-editor/apply/Delete`, {
            target: `#bulk-editor`,
            swap: "outerHTML",
          });
          break;
      }
    }
  }
});
