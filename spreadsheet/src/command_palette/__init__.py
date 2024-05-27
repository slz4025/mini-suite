from flask import render_template

import src.bulk_editor as bulk_editor
import src.editor as editor
import src.port.viewer as viewer
import src.selector as selector

import src.command_palette.state as state


def render(session):
    show_command_palette = state.get_show(session)
    show_help = state.get_show_help(session)

    editor_html = editor.render(session)
    selector_html = selector.render(session)
    bulk_editor_html = bulk_editor.render(session)
    viewer_html = viewer.render(session)

    command_palette = render_template(
            "partials/command_palette.html",
            show_command_palette=show_command_palette,
            show_help=show_help,
            editor=editor_html,
            selector=selector_html,
            bulk_editor=bulk_editor_html,
            viewer=viewer_html,
    )
    return command_palette


def init(session):
    show = False
    state.set_show(session, show)

    show_help = False
    state.set_show_help(session, show_help)
    show_editor = False
    state.set_show_editor(session, show_editor)
    show_selector = False
    state.set_show_selector(session, show_selector)
    show_bulk_editor = False
    state.set_show_bulk_editor(session, show_bulk_editor)
    show_viewer = False
    state.set_show_viewer(session, show_viewer)
