from dataclasses import dataclass
from flask import render_template

import src.modes as modes


@dataclass
class Settings:
    render_mode: str
    mrows: int
    mcols: int
    nrows: int
    ncols: int


def init(session):
    render_mode = "light"
    mrows = 5
    mcols = 5
    nrows = 30
    ncols = 15

    set(
        session,
        render_mode=render_mode,
        mrows=mrows,
        mcols=mcols,
        nrows=nrows,
        ncols=ncols,
    )


def set(
    session,
    render_mode=None,
    mrows=None,
    mcols=None,
    nrows=None,
    ncols=None,
):
    if render_mode is not None:
        session["render-mode"] = render_mode
    if mrows is not None:
        session["mrows"] = str(mrows)
    if mcols is not None:
        session["mcols"] = str(mcols)
    if nrows is not None:
        session["nrows"] = str(nrows)
    if ncols is not None:
        session["ncols"] = str(ncols)


def get(session):
    render_mode = session["render-mode"]
    mrows = int(session["mrows"])
    mcols = int(session["mcols"])
    nrows = int(session["nrows"])
    ncols = int(session["ncols"])

    return Settings(
        render_mode=render_mode,
        mrows=mrows,
        mcols=mcols,
        nrows=nrows,
        ncols=ncols,
    )


def render(session):
    settings_state = modes.check(session, "Settings")
    current_settings = get(session)

    return render_template(
        "partials/settings.html",
        show_settings=settings_state,
        render_mode=current_settings.render_mode,
        mrows=current_settings.mrows,
        mcols=current_settings.mcols,
        nrows=current_settings.nrows,
        ncols=current_settings.ncols,
    )
