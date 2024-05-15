function editing() {
  const activeId = document.activeElement.id;
  if (activeId == "editor-contents") {
    return true;
  }
  else if (activeId == "value-contents") {
    return true;
  }
  else if (activeId.startsWith("input-cell-")) {
    return true;
  }
  else {
    return false;
  }
}

function update_editor(row, col) {
    htmx.ajax('PUT', `/cell/${row}/${col}/focus`, {
      target: "#editor",
      swap: "outerHTML",
    });
}

function render_reset_focus() {
  // Reset all visible cells so don't have to record
  // last focused cell nor retrieve it from the backend
  // when reopen frontend.
  const cells = get_cells();
  cells.forEach((cell) => {
    cell.classList.remove("editing-current");
  });
}

function render_focus(row, col) {
  const e = document.querySelector(`#${get_cell_id(row, col)}`);
  e.classList.add("editing-current");
}

// acts like a queue
const edit_request_buffer = [];

function request_change_focus(row, col) {
  render_reset_focus();
  render_focus(row, col);

  edit_request_buffer.push([row, col]);
};

function _change_editor() {
  let request = undefined;
  while (edit_request_buffer.length > 0) {
    request = edit_request_buffer.shift();
  }

  if (!request) {
    return;
  }

  const [row, col] = request;
  update_editor(row, col);
}
// Interval should be about the duration it takes to return from the backend.
setInterval("_change_editor()", 500);