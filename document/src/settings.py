from flask import render_template


DARK_MODE = None


def get_dark_mode():
    return DARK_MODE


def set_dark_mode(dark_mode):
    global DARK_MODE
    DARK_MODE = dark_mode


def render_mode_button(session):
    dark_mode = get_dark_mode()
    return render_template(
            "partials/mode_button.html",
            dark_mode=dark_mode,
            )


def init():
    set_dark_mode(False)
