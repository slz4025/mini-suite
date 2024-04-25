var trial_selection = undefined;
function init_trial_selection(start_row, start_col) {
  trial_selection = [start_row, start_col, start_row, start_col];
}
function get_trial_selection() {
  return trial_selection;
}
function update_trial_selection(end_row, end_col) {
  const [start_row, start_col, , ] = get_trial_selection();
  trial_selection = [start_row, start_col, end_row, end_col];
}
function reset_trial_selection() {
  trial_selection = undefined;
}
function in_selection() {
  return get_trial_selection() != undefined;
}
function is_valid_selection(end_row, end_col) {
  const [start_row, start_col, , ] = get_trial_selection();

  const start_cell_id = get_cell_id(start_row, start_col);
  const start_cell_type = get_cell_type(start_cell_id);

  const end_cell_id = get_cell_id(end_row, end_col);
  const end_cell_type = get_cell_type(end_cell_id);

  return start_cell_type == end_cell_type;
}
function render_trial_selection(end_row, end_col) {
  const [start_row, start_col, prev_end_row, prev_end_col] = 
    get_trial_selection();

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

  const left_diff = new Set([...prev_set].filter(x => !curr_set.has(x)));
  const right_diff = new Set([...curr_set].filter(x => !prev_set.has(x)));

  const cells_to_default = [...left_diff];
  const cells_to_trial = [...right_diff];

  cells_to_default.forEach(([row, col]) => {
    const e = document.querySelector(`#${get_cell_id(row, col)}`);
    e.style.border = '';
  });

  const style = getComputedStyle(document.documentElement);
  const trial_selected_color = style.getPropertyValue('--selected-trial-color');
  const trial_selected_state = `1px solid ${trial_selected_color}`;

  cells_to_trial.forEach(([row, col]) => {
    const e = document.querySelector(`#${get_cell_id(row, col)}`);
    e.style.border = trial_selected_state;
  });
}

function render_reset_selection() {
  const pointers = get_pointers();
  pointers.forEach((pointer) => {
    pointer.style.display = "none";
  });

  const row_headers = get_row_headers();
  const col_headers = get_col_headers();
  const headers = row_headers.concat(col_headers);
  headers.forEach((header) => {
    header.style.border = "";
    header.classList.remove("selected-next-row");
    header.classList.remove("selected-next-col");
  });

  const cells = get_cells();
  cells.forEach((cell) => {
    cell.style.border = "";
    cell.style["background-color"] = "";
    cell.classList.remove("selected-next-row");
    cell.classList.remove("selected-next-col");
    cell.classList.remove("selected-current");
  });
}

function render_selection() {
  const [start_row, start_col, end_row, end_col] = get_trial_selection();

  const effective_start_row = Math.min(start_row, end_row);
  const effective_end_row = Math.max(start_row, end_row);
  const effective_start_col = Math.min(start_col, end_col);
  const effective_end_col = Math.max(start_col, end_col);

  const curr_set = new Set();
  if (effective_start_col == -1) {
    for (let i = effective_start_row; i <= effective_end_row; i++) {
      get_cells_by_row(i).forEach(e => curr_set.add(e));
    }
  } else if (effective_start_row == -1) {
    for (let j = effective_start_col; j <= effective_end_col; j++) {
      get_cells_by_col(j).forEach(e => curr_set.add(e));
    }
  } else {
    for (let i = effective_start_row; i <= effective_end_row; i++) {
      for (let j = effective_start_col; j <= effective_end_col; j++) {
        curr_set.add(document.querySelector(`#${get_cell_id(i, j)}`));
      }
    }
  }
  const selection_cells = [...curr_set];

  const style = getComputedStyle(document.documentElement);
  const selected_finalized_state =
    style.getPropertyValue('--selected-background-color');

  selection_cells.forEach((cell) => {
    cell.style["background-color"] = selected_finalized_state;
  });
}

function apply_selection() {
  render_reset_selection();
  render_selection();

  const [start_row, start_col, end_row, end_col] = get_trial_selection();
  htmx.ajax(
    'PUT',
    `/selection/start/${start_row}/${start_col}/end/${end_row}/${end_col}`,
    {
      target: "#selection",
      swap: "outerHTML",
    }
  );
}

// Javascript is single-threaded and finishes one function
// before starting another, i.e. due to incoming event.
// Each of the request functions should therefore not be interrupted.

function begin_selection(start_row, start_col) {
  init_trial_selection(start_row, start_col);
}

function finalize_selection(end_row, end_col) {
  if (!is_valid_selection(end_row, end_col)) {
    reset_trial_selection();
    return;
  }

  update_trial_selection(end_row, end_col);

  apply_selection();

  reset_trial_selection();
}

// acts like a queue
const selection_request_buffer = [];

function request_change_selection(end_row, end_col) {
  if (!in_selection()) {
    return;
  }

  const [ , , prev_end_row, prev_end_col] = get_trial_selection();
  if (end_row == prev_end_row && end_col == prev_end_col) {
    return;
  }

  if (!is_valid_selection(end_row, end_col)) {
    return;
  }

  selection_request_buffer.push([end_row, end_col]);
};

function _change_selection() {
  let request = undefined;
  while (selection_request_buffer.length > 0) {
    request = selection_request_buffer.shift();
  }

  if (!request) {
    return;
  }

  const [end_row, end_col] = request;

  render_trial_selection(end_row, end_col);
  update_trial_selection(end_row, end_col);
}
setInterval("_change_selection()", 25);
