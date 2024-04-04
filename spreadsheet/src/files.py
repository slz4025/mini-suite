from flask import render_template
import json
import os
import numpy as np
import pandas as pd
from io import StringIO

import src.command_palette as command_palette
import src.data.sheet as sheet
import src.errors as errors


DOWNLOADS_DIR = os.path.expanduser("~/Downloads")


def import_from(request):
    if 'input' not in request.files:
        raise errors.UserError("File was not chosen.")
    file = request.files['input']

    filename = file.filename
    if not filename.endswith(".csv"):
        raise errors.UserError("File is not a csv file.")

    contents = file.read().decode("utf-8")
    buffer = StringIO(contents)
    df = pd.read_csv(buffer, quotechar='"', skipinitialspace=True, header=None)
    data = df.to_numpy()

    sheet.set(data)


def export_to(request):
    filename = request.form["input"]
    if filename == '':
        raise errors.UserError("Filename not given.")

    data = sheet.get()

    filepath = os.path.join(DOWNLOADS_DIR, f"{filename}.csv")
    np.savetxt(filepath, data, delimiter=",", fmt="%s")


def open_from(request):
    if 'input' not in request.files:
        raise errors.UserError("File was not chosen.")
    file = request.files['input']

    filename = file.filename
    if not filename.endswith(".sheet"):
        raise errors.UserError("File is not a sheet file.")

    contents = file.read().decode("utf-8")
    try:
        sheet_data = json.loads(contents)
    except json.decoder.JSONDecodeError as e:
        raise errors.UserError(f"File is corrupted: not proper JSON: {e}.")

    try:
        num_rows = sheet_data["num_rows"]
        num_cols = sheet_data["num_cols"]
        data = np.empty((num_rows, num_cols), dtype=object)

        cells = sheet_data["cells"]
        for cell in cells:
            row = cell["row"]
            col = cell["col"]
            value = cell["value"]
            data[row, col] = value

    except KeyError as e:
        raise errors.UserError(f"File is corrupted: missing key {e}.")

    sheet.set(data)


def save_to(request):
    filename = request.form["input"]
    if filename == '':
        raise errors.UserError("Filename not given.")

    data = sheet.get()
    num_rows = data.shape[0]
    num_cols = data.shape[1]

    cells = []
    for row in range(num_rows):
        for col in range(num_cols):
            if data[row, col] is None:
                continue
            value = data[row, col]
            cell = {
                "row": row,
                "col": col,
                "value": value,
            }
            cells.append(cell)

    sheet_data = {}
    sheet_data["num_rows"] = num_rows
    sheet_data["num_cols"] = num_cols
    sheet_data["cells"] = cells
    contents = json.dumps(sheet_data)

    filepath = os.path.join(DOWNLOADS_DIR, f"{filename}.sheet")
    with open(filepath, 'w+') as file:
        file.write(contents)


def render(session):
    show_files = command_palette.get_show_files(session)

    return render_template(
        "partials/files.html",
        show_files=show_files,
    )
