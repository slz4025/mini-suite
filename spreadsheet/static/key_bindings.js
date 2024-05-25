window.addEventListener('keydown', function(event) {
  const focused_cell = get_focused_cell();
  if (focused_cell != undefined) {
    const [row, col] = focused_cell;

    // The native behavior is that
    // Tab goes right or next
    // and Shift-Tab goes left or previous.
    // We therefore only encode the desired behavior
    // for Enter (down) and Shift-Enter (up).
    let nextId;
    if (event.shiftKey) {
      switch (event.key) {
        case 'Enter':
          event.preventDefault();
          nextId = `cell-${row-1}-${col}`;
          break;
      }
    } else {
      switch (event.key) {
        case 'Enter':
          event.preventDefault();
          nextId = `cell-${row+1}-${col}`;
          break;
      }
    }

    const element = document.getElementById(nextId);
    if (element) {
      element.focus();
    }
  } else {
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

        // view
        case 'h':
          document.getElementById("home-button").click();
          break;
        case 't':
          document.getElementById("navigator-target-button").click();
          break;

        // save
        case 's':
          document.getElementById("files-save").click();
          break;
      }
    } else if (event.shiftKey) {
      switch (event.key) {
        // view
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

        // selection
        case 'W':
          document.getElementById("up-selection-button")?.click();
          break;
        case 'S':
          document.getElementById("down-selection-button")?.click();
          break;
        case 'A':
          document.getElementById("left-selection-button")?.click();
          break;
        case 'D':
          document.getElementById("right-selection-button")?.click();
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
  }
});
