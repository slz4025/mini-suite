window.addEventListener('keyup', function(event) {
  if (event.shiftKey) {
    switch (event.key) {
      case 'Enter':
        htmx.ajax('POST', "/block/unfocus", {
          target: "#blocks",
          swap: "outerHTML",
        });
        break;
      case 'ArrowUp':
        htmx.ajax('POST', "/block/prev", {
          target: "#blocks",
          swap: "outerHTML",
        });
        break;
      case 'ArrowDown':
        htmx.ajax('POST', "/block/next", {
          target: "#blocks",
          swap: "outerHTML",
        });
        break;
    }
  }
});
