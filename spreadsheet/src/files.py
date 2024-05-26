from flask import render_template
import json
import os
import numpy as np
import pandas as pd

import src.computer as computer
import src.sheet as sheet
import src.errors as errors


FILE_PATH = None


def setup(filepath, debug):
    global FILE_PATH

    if not filepath.endswith(".csv"):
        raise errors.UserError("File is not a csv file.")
    FILE_PATH = filepath

    if os.path.exists(FILE_PATH):
        open()
    else:
        sheet.init(debug)


def open():
    df = pd.read_csv(
        FILE_PATH,
        skipinitialspace=True,
        header=None,
        dtype=object,
    )
    df.fillna("", inplace=True)
    data = df.to_numpy()
    sheet.set(data)


def safe_format(data):
    num_rows = data.shape[0]
    num_cols = data.shape[1]

    converted = np.empty((num_rows, num_cols), dtype=object)
    for i in range(num_rows):
        for j in range(num_cols):
            entry = data[i, j]
            if entry is not None:
                converted[i, j] = json.dumps(entry)
            else:
                converted[i, j] = ""
    return converted


def save():
    data = sheet.get()
    converted = safe_format(data)

    np.savetxt(FILE_PATH, converted, delimiter=",", fmt="%s")
