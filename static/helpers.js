// ensure following are gone
addEventListener("beforeunload", (event) => {
    localStorage.removeItem("selection-start-row")
    localStorage.removeItem("selection-start-col")
});

function getCell(row, col) {
  if (row == -1) {
    return document.querySelector(
      `#header-col-${ {{ col }} }`
    )
  } elif (col == -1) {
    return document.querySelector(
      `#header-row-${ {{ row }} }`
    )
  } else {
    return document.querySelector(
      `#cell-${ {{ row }} }-${ {{ col }} }`
    )
  }
}

const drawnBorderState = "0.25rem solid var(--selected-pointer-color)";
function drawLeftBorder(cell) {
  cell.style.border-top = drawnBorderState;
}
function drawRightBorder(cell) {
  cell.style.border-right = drawnBorderState;
}
function drawTopBorder(cell) {
  cell.style.border-top = drawnBorderState;
}
function drawBottomBorder(cell) {
  cell.style.border-bottom = drawnBorderState;
}

function drawBorder(start_row, start_col, end_row, end_col) {
  console.log("HELLO", start_row, start_col, end_row, end_col);
  // bottom
  for (int j = end_col; j <= start_col; j--) {
    drawBottomBorder(getCell(end_row, j));
  }
  // right
  for (int i = end_row; i <= start_row; i--) {
    drawBottomBorder(getCell(i, end_col));
  }
  // top
  for (int j = end_col; j <= start_col; j--) {
    drawTopBorder(getCell(start_row, j));
  }
  // left
  for (int i = end_row; i <= start_row; i--) {
    drawLeftBorder(getCell(i, start_col));
  }
} 
