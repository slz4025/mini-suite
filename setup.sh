#!/bin/bash

repo_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Setting up document editor..."
doc_dir="${repo_dir}/document"
cd "${doc_dir}"
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
echo "Finished setting up document editor."
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
