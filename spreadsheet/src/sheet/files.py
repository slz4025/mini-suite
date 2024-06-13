import csv
from flask import render_template
import os
import numpy as np

import src.errors.types as err_types

import src.sheet.compiler as compiler
import src.sheet.data as sheet_data


FILE_PATH = None


def setup(filepath, debug):
    global FILE_PATH

    if not filepath.endswith(".csv"):
        raise err_types.UserError("Input file is not a csv file.")
    FILE_PATH = filepath

    if os.path.exists(FILE_PATH):
        open_file()
    else:
        sheet_data.init(debug)


# csv file to numpy array of Python values
def open_file():
    # set newline='' so can properly handle newlines in strings
    with open(FILE_PATH, newline='') as file:
        reader = csv.reader(file, delimiter=',', quoting=csv.QUOTE_ALL)
        data = np.array([row for row in reader], dtype=object)
        sheet_data.set(data)


# numpy array of Python values to csv file
def save():
    # set newline='' so can properly handle newlines in strings
    with open(FILE_PATH, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_ALL)
        data = sheet_data.get()
        writer.writerows(data)
