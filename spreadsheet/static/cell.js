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

  var arr;
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

function get_cell_type(id) {
  if (id.startsWith('header-row-')) {
    return 'ROW_HEADER';
  } else if (id.startsWith('header-col-')) {
    return 'COL_HEADER';
  } else {
    return 'CELL';
  }
}

function get_row_headers() {
  const query = document.querySelectorAll('[id^="header-row-"]');
  return [...query];
}

function get_col_headers() {
  const query = document.querySelectorAll('[id^="header-col-"]');
  return [...query];
}

function get_cells() {
  const query = document.querySelectorAll('[id^="cell-"]');
  return [...query];
}

function get_cells_by_row(row) {
  return get_cells().filter((cell) => {
    const id = cell.id;
    const re = new RegExp(`cell-${row}-([0-9]+)`);
    return re.test(id);
  });
}

function get_cells_by_col(col) {
  return get_cells().filter((cell) => {
    const id = cell.id;
    const re = new RegExp(`cell-([0-9]+)-${col}`);
    return re.test(id);
  });
}

function get_pointers() {
  const query = document.querySelectorAll('[id$="-pointer"]');
  return [...query];
}
