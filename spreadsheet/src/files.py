from flask import render_template
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


def render(session):
    show_files = command_palette.get_show_files(session)

    return render_template(
        "partials/files.html",
        show_files=show_files,
    )
