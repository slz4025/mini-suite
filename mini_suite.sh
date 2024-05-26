#!/bin/bash

MIN_PORT=15000
MAX_PORT=25000

repo_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

get_port() {
    available_port=0
    for port in {$MIN_PORT..$MAX_PORT}
    do
        if ! nc -z 127.0.0.1 ${port} > /dev/null 2>&1; then
            available_port=${port}
            break
        fi
    done

    if [ "${available_port}" -eq "0" ]; then
        echo "Cannot find unused port to run program."
        exit 1
    fi

    echo ${available_port}
}

make_logfile() {
    prefix="$1"
    timestamp=$(date +%s)
    logfile="/tmp/${prefix}-${timestamp}"
    touch "${logfile}"
    echo "${logfile}"
}

_sheet() {
    sheet_dir="$1"
    port="$2"
    file="$3"
    logfile="$4"

    source "${sheet_dir}/.venv/bin/activate"
    python "${sheet_dir}/spreadsheet.py" --port "${port}" "${file}" > "${logfile}" 2>&1
}

sheet() {
    sheet_dir="${repo_dir}/spreadsheet"
    port=$(get_port)
    file="$1"
    logfile=$(make_logfile "sheet")

    _sheet "${sheet_dir}" "${port}" "${file}" "${logfile}" &

    echo "Visit localhost:${port} to edit your spreadsheet file."
    echo "Tailing server output in ${logfile}"
    tail -f "${logfile}"
}

_doc() {
    doc_dir="$1"
    port="$2"
    option="$3"
    doc_path="$4"
    logfile="$5"

    source "${doc_dir}/.venv/bin/activate"
    python "${doc_dir}/document.py" --port "${port}" "${option}" "${doc_path}" > "${logfile}" 2>&1
}

doc() {
    doc_dir="${repo_dir}/document"
    port=$(get_port)
    file="$1"
    logfile=$(make_logfile "doc")

    _doc "${doc_dir}" "${port}" "file" "${file}" "${logfile}" &

    echo "Visit localhost:${port} to edit your markdown file."
    echo "Tailing server output in ${logfile}"
    tail -f "${logfile}"
}

wiki() {
    doc_dir="${repo_dir}/document"
    port=$(get_port)
    dir="$1"
    logfile=$(make_logfile "wiki")

    _doc "${doc_dir}" "${port}" "wiki" "${dir}" "${logfile}" &

    echo "Visit localhost:${port} to edit your wiki."
    echo "Tailing server output in ${logfile}"
    tail -f "${logfile}"
}
