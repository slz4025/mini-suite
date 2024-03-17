window.addEventListener('keyup', function(event) {
  if (event.ctrlKey) {
    switch (event.key) {
      case 'ArrowUp':
        htmx.ajax('POST', `/block/prev`, {
          target: `#blocks`,
          swap: "outerHTML",
        });
        break;
      case 'ArrowDown':
        htmx.ajax('POST', `/block/next`, {
          target: `#blocks`,
          swap: "outerHTML",
        });
        break;
    }
  }
});
