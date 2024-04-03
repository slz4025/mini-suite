function editing() {
  const activeId = document.activeElement.id;
  if (activeId == "editor-contents") {
    return true;
  }
  else if (activeId.startsWith("input-cell-")) {
    return true;
  }
  else {
    return false;
  }
}
