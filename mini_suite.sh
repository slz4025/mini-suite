#!/bin/bash

sheet() {
    sheet_dir="${MINISUITE_PATH}/spreadsheet"
    source "${sheet_dir}/.venv/bin/activate"
    python "${sheet_dir}/spreadsheet.py" --port 5001 "$@"
}

doc() {
    doc_dir="${MINISUITE_PATH}/document"
    source "${doc_dir}/.venv/bin/activate"
    python "${doc_dir}/document.py" --port 5000 "$@"
}
