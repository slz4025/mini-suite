from flask import render_template

import src.entry as entry
import src.settings as settings


def render(session):
    entry_name = entry.get(allow_temp=False)
    mode_button_html = settings.render_mode_button(session)
    return render_template(
            "partials/command_palette.html",
            current_entry=entry_name if entry_name is not None else '',
            mode_button=mode_button_html,
            )
