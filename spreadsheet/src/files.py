from flask import render_template

import src.command_palette as command_palette


def render(session):
    show_files = command_palette.get_show_files(session)

    return render_template(
        "partials/files.html",
        show_files=show_files,
    )
