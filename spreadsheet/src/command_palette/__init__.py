from flask import render_template

import src.bulk_editor as bulk_editor
import src.editor as editor
import src.viewer as viewer
import src.selector as selector

import src.command_palette.state as state


def render():
    show_command_palette = state.get_show()
    show_help = state.get_show_help()

    editor_html = editor.render()
    selector_html = selector.render()
    bulk_editor_html = bulk_editor.render()
    viewer_html = viewer.render()

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
