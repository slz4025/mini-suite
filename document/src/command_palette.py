from flask import render_template

import src.entry as entry
import src.selector as selector
import src.settings as settings


SHOW = None


def get_show():
    return SHOW


def set_show(show):
    global SHOW
    SHOW = show


def init():
    set_show(True)


def render_open(session):
    open_entry_selector = selector.render(
        session,
        operation="open",
    )
    return render_template(
            "partials/command_palette/open.html",
            open_entry_selector=open_entry_selector,
            )


def render_import(session):
    return render_template(
            "partials/command_palette/import.html",
            )


def render_export(session):
    return render_template(
            "partials/command_palette/export.html",
            )


def render_operation(session, operation):
    match operation:
        case 'open':
            return render_open(session)
        case 'import':
            return render_import(session)
        case 'export':
            return render_export(session)
        case _:
            raise Exception(
                f"'{operation}' is not a command palette "
                "input/output operation."
            )


def render(session):
    show = get_show()
    entry_name = entry.get(allow_temp=False)
    mode_button_html = settings.render_mode_button(session)
    return render_template(
            "partials/command_palette.html",
            show=show,
            current_entry=entry_name if entry_name is not None else '',
            mode_button=mode_button_html,
            )
