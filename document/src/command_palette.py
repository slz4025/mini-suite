from flask import render_template


SHOW = None


def get_show():
    return SHOW


def set_show(show):
    global SHOW
    SHOW = show


def init(show):
    set_show(show)


def render(session):
    show = get_show()
    return render_template(
            "partials/command_palette.html",
            show=show,
            )
