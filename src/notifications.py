from dataclasses import dataclass
from enum import Enum
from flask import render_template

import src.errors as errors
import src.modes as modes


class Mode(Enum):
    NONE = "none"
    INFO = "info"
    WARN = "warning"
    ERROR = "error"


@dataclass
class Notification:
    message: str
    mode: Mode


def get(session):
    message = session["notification-message"]
    raw_mode = session["notification-mode"]
    try:
        mode = Mode(raw_mode)
    except ValueError:
        raise errors.UnknownOptionError(
            f"'{raw_mode}' is not a valid notification mode."
        )
    return Notification(message=message, mode=mode)


def set(session, notification):
    session["notification-message"] = notification.message
    session["notification-mode"] = notification.mode.value


def reset(session):
    notification = Notification(message="", mode=Mode.NONE)
    set(session, notification)


def init(session):
    reset(session)


def render(session, show):
    notification = get(session)
    return render_template(
        "partials/notification_banner.html",
        modes=modes.get_str(session),
        message=notification.message,
        mode=notification.mode.value,
        show=show,
    )
