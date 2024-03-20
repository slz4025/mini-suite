from flask import render_template

import src.entry as entry
import src.settings as settings


SHOW = None


def get_show():
    return SHOW


def set_show(show):
    global SHOW
    SHOW = show


def init():
    set_show(True)


def render(session):
    show = get_show()
    entry_name = entry.get(allow_temp=False)
    open_entry_selector = entry.render_selector(session)
    mode_button_html = settings.render_mode_button(session)
    return render_template(
            "partials/command_palette.html",
            show=show,
            current_entry=entry_name if entry_name is not None else '',
            open_entry_selector=open_entry_selector,
            mode_button=mode_button_html,
            )
