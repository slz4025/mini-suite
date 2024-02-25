from dataclasses import dataclass


@dataclass
class Settings:
    render_mode: str
    mrows: int
    mcols: int
    nrows: int
    ncols: int


def init_settings(session):
    render_mode = "light"
    mrows = 5
    mcols = 5
    nrows = 30
    ncols = 15

    set_settings(
        session,
        render_mode=render_mode,
        mrows=mrows,
        mcols=mcols,
        nrows=nrows,
        ncols=ncols,
    )


def set_settings(
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


def get_settings(session):
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
