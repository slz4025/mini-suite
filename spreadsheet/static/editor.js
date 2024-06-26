// Should be the only one with the 'editing-current' class.
var focused_cell = undefined;
function get_focused_cell() {
  return focused_cell;
}
function set_focused_cell(fc) {
  if (fc === undefined) {
    // Remove class from previous.
    if (focused_cell !== undefined) {
      const [row, col] = focused_cell;
      const id = get_cell_id(row, col);
      const e = document.querySelector(`#${id}`);
      e.classList.remove("editing-current");
    }
  } else {
    // Add class to new.
    const [row, col] = fc;
    const id = get_cell_id(row, col);
    const e = document.querySelector(`#${id}`);
    e.classList.add("editing-current");
  }

  focused_cell = fc;
}

// Find the cell we intend to edit.
// This is based on the 'editing-current' class that we update immediately on the frontend.
function get_focused_cell() {
  const cells = get_cells();
  const focused_cells = cells.filter((cell) => {
    return cell.classList.contains('editing-current');
  });
  if (focused_cells.length === 0) {
    return undefined;
  } else {
    const focused_cell = focused_cells[0];
    // A cell has an id like 'cell-<row>-<col>'.
    var arr = focused_cell.id.split('-');
    const row = Number(arr[1]);
    const col = Number(arr[2]);
    return [row, col];
  }
}

async function update_focus(row, col) {
  await htmx.ajax('POST', `/cell/${row}/${col}/focus`, {
    target: `#cell-${row}-${col}`,
    swap: "outerHTML",
  });

  const e = document.querySelector(`#input-cell-${row}-${col}`);
  e.focus();
}

function render_reset_focus() {
  // Reset if stored on frontend.
  set_focused_cell(undefined);

  // Reset if not stored on frontend.
  // This happens if we reopen the frontend
  // but still have the backend running
  // and maintaining state.
  const cells = get_cells();
  cells.forEach((cell) => {
    cell.classList.remove("editing-current");
  });
}

function render_focus(row, col) {
  set_focused_cell([row, col]);
}

// acts like a queue
const edit_request_buffer = [];

function request_change_focus(row, col) {
  render_reset_focus();
  render_focus(row, col);

  edit_request_buffer.push([row, col]);
};

async function _change_editor() {
  let request = undefined;
  while (edit_request_buffer.length > 0) {
    request = edit_request_buffer.shift();
  }

  if (!request) {
    return;
  }

  const [row, col] = request;
  await update_focus(row, col);
}
// Interval should be about the duration it takes to return from the backend.
setInterval("_change_editor()", 100);
