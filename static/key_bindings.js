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
        document.getElementById("bulk-edit-toggler").click();
        break;
      case '3':
        document.getElementById("navigator-toggler").click();
        break;
      case '4':
        document.getElementById("settings-toggler").click();
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
    }
  }
});
