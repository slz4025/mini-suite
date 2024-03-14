var selection_start_row = undefined;
var selection_start_col = undefined;
function set_selection_start(row, col) {
  selection_start_row = Number(row);
  selection_start_col = Number(col);
}
function reset_selection_start() {
  selection_start_row = undefined;
  selection_start_col = undefined;
}
function get_selection_start() {
  return [selection_start_row, selection_start_col];
}

var selection_end_row = undefined;
var selection_end_col = undefined;
function set_selection_end(row, col) {
  selection_end_row = Number(row);
  selection_end_col = Number(col);
}
function reset_selection_end() {
  selection_end_row = undefined;
  selection_end_col = undefined;
}
function get_selection_end() {
  return [selection_end_row, selection_end_col];
}

function get_cell_id(row, col) {
  var id;
  if (col == -1) {
    id = `header-row-${row}`;
  } else if (row == -1) {
    id = `header-col-${col}`;
  } else {
    id = `cell-${row}-${col}`;
  }
  return id;
}

function get_position(id) {
  let row = -1;
  let col = -1;

  if (id.startsWith('header-row-')) {
    arr = id.match(/header-row-([0-9]+)/);
    row = Number(arr[1]);
  } else if (id.startsWith('header-col-')) {
    arr = id.match(/header-col-([0-9]+)/);
    col = Number(arr[1]);
  } else if (id.startsWith('cell-')) {
    arr = id.match(/cell-([0-9]+)-([0-9]+)/);
    row = Number(arr[1]);
    col = Number(arr[2]);
  }

  return [row, col];
}

function valid_selection(end_row, end_col) {
  const start_cell_id = get_cell_id(selection_start_row, selection_start_col);
  const end_cell_id = get_cell_id(end_row, end_col);

  if (
    start_cell_id.startsWith('header-row-')
    && end_cell_id.startsWith('header-row-')
  ) {
    return true;
  } else if (
    start_cell_id.startsWith('header-col-')
    && end_cell_id.startsWith('header-col-')
  ) {
    return true;
  } else if (
    start_cell_id.startsWith('cell-')
    && end_cell_id.startsWith('cell-')
  ) {
    return true;
  } else {
    return false;
  }
}

function compute_cells_to_update(end_row, end_col) {
  const [start_row, start_col] = get_selection_start();
  const [prev_end_row, prev_end_col] = get_selection_end();

  const prev_effective_start_row = Math.min(start_row, prev_end_row);
  const prev_effective_end_row = Math.max(start_row, prev_end_row);
  const prev_effective_start_col = Math.min(start_col, prev_end_col);
  const prev_effective_end_col = Math.max(start_col, prev_end_col);

  const effective_start_row = Math.min(start_row, end_row);
  const effective_end_row = Math.max(start_row, end_row);
  const effective_start_col = Math.min(start_col, end_col);
  const effective_end_col = Math.max(start_col, end_col);


  const prev_set = new Set();
  for (let i = prev_effective_start_row; i <= prev_effective_end_row; i++) {
    for (let j = prev_effective_start_col; j <= prev_effective_end_col; j++) {
      prev_set.add([i, j]);
    }
  }

  const curr_set = new Set();
  for (let i = effective_start_row; i <= effective_end_row; i++) {
    for (let j = effective_start_col; j <= effective_end_col; j++) {
      curr_set.add([i, j]);
    }
  }

  const leftDiff = new Set([...prev_set].filter(x => !curr_set.has(x)));
  const rightDiff = new Set([...curr_set].filter(x => !prev_set.has(x)));

  return [[...leftDiff], [...rightDiff]];
}

async function default_cells(arr) {
  await Promise.all(arr.map(async ([row, col]) => {
    const e = document.querySelector(`#${get_cell_id(row, col)}`);
    e.style.border = '';
  }));
}

const style = getComputedStyle(document.documentElement);
const selected_color = style.getPropertyValue('--selected-pointer-color');
const selected_state = `1px solid ${selected_color}`;
async function select_cells(arr) {
  await Promise.all(arr.map(async ([row, col]) => {
    const e = document.querySelector(`#${get_cell_id(row, col)}`);
    e.style.border = selected_state;
  }));
}

// acts like a queue
const request_buffer = [];

function request_change_selection(end_row, end_col) {
  if (!selection_start_row || !selection_start_col) {
    return;
  }

  if (end_row == selection_end_row && end_col == selection_end_col) {
    return;
  }

  if (!valid_selection(end_row, end_col)) {
    return;
  }

  request_buffer.push([end_row, end_col]);
};

async function _change_selection() {
  let request = undefined;
  while (request_buffer.length > 0) {
    request = request_buffer.shift();
  }

  if (!request) {
    return;
  }

  const [end_row, end_col] = request;

  const [to_default, to_selected] = compute_cells_to_update(end_row, end_col);
  await default_cells(to_default);
  await select_cells(to_selected);

  set_selection_end(end_row, end_col);
}
setInterval("_change_selection()", 25);
