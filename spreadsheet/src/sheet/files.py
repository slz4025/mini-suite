from flask import render_template
import json
import os
import numpy as np
import pandas as pd

import src.errors.types as err_types

import src.sheet.compiler as compiler
import src.sheet.data as sheet_data


FILE_PATH = None


def setup(filepath, debug):
    global FILE_PATH

    if not filepath.endswith(".csv"):
        raise err_types.UserError("File is not a csv file.")
    FILE_PATH = filepath

    if os.path.exists(FILE_PATH):
        open()
    else:
        sheet_data.init(debug)


def load(data):
    num_rows = data.shape[0]
    num_cols = data.shape[1]

    converted = np.empty((num_rows, num_cols), dtype=object)
    for i in range(num_rows):
        for j in range(num_cols):
            entry = data[i, j]
            if np.isnan(entry):
              entry = None
            converted[i, j] = compiler.cast(entry)
    return converted


def dump(data):
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


def open():
    df = pd.read_csv(
        FILE_PATH,
        skipinitialspace=True,
        header=None,
        dtype=object,
    )
    data = df.to_numpy()
    converted = load(data)

    sheet_data.set(converted)


def save():
    data = sheet_data.get()
    converted = dump(data)

    np.savetxt(FILE_PATH, converted, delimiter=",", fmt="%s")
