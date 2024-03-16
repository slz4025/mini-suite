from dataclasses import dataclass
from flask import render_template

import src.modes as modes


@dataclass
class Settings:
    render_mode: str


def init(session):
    render_mode = "light"

    set(
        session,
        render_mode=render_mode,
    )


def set(
    session,
    render_mode=None,
):
    if render_mode is not None:
        session["render-mode"] = render_mode


def get(session):
    render_mode = session["render-mode"]

    return Settings(
        render_mode=render_mode,
    )


def render(session):
    settings_state = modes.check(session, "Settings")
    current_settings = get(session)

    return render_template(
        "partials/settings.html",
        show_settings=settings_state,
        render_mode=current_settings.render_mode,
    )
