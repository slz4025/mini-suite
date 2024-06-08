#!/bin/bash

sheet() {
    sheet_dir="${MINISUITE_PATH}/spreadsheet"
    source "${sheet_dir}/.venv/bin/activate"
    python "${sheet_dir}/spreadsheet.py" "$@"
}

doc() {
    doc_dir="${MINISUITE_PATH}/document"
    source "${doc_dir}/.venv/bin/activate"
    python "${doc_dir}/document.py" file "$@"
}

wiki() {
    doc_dir="${MINISUITE_PATH}/document"
    source "${doc_dir}/.venv/bin/activate"
    python "${doc_dir}/document.py" wiki "$@"
}
