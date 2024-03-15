from flask import render_template

import src.bulk_editor as bulk_editor
import src.editor as editor
import src.navigator as navigator
import src.selection as selection
import src.settings as settings


def get_show(session):
    show = bool(session["show-command-palette"])
    return show


def set_show(session, show):
    session["show-command-palette"] = show


def render(session):
    show_command_palette = get_show(session)
    editor_html = editor.render(session)
    selection_html = selection.render(session)
    bulk_editor_html = bulk_editor.render(session)
    navigator_html = navigator.render(session)
    settings_html = settings.render(session)
    command_palette = render_template(
            "partials/command_palette.html",
            show_command_palette=show_command_palette,
            editor=editor_html,
            selection=selection_html,
            bulk_editor=bulk_editor_html,
            navigator=navigator_html,
            settings=settings_html,
    )
    return command_palette


def init(session):
    show = True
    set_show(session, show)
