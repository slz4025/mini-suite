#!/bin/bash

repo_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Setting up markdown editor..."
doc_dir="${repo_dir}/document"
cd "${doc_dir}"
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
echo "Finished setting up markdown editor."
echo ""

echo "Setting up spreadsheet editor..."
sheet_dir="${repo_dir}/spreadsheet"
cd "${sheet_dir}"
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
echo "Finished setting up spreadsheet editor."
echo ""
