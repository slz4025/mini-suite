from dataclasses import dataclass
from enum import Enum
from flask import render_template

from src.errors import UnknownOptionError
from src.modes import get_modes_str


class NotificationMode(Enum):
    NONE = "none"
    INFO = "info"
    WARN = "warning"
    ERROR = "error"


@dataclass
class Notification:
    message: str
    mode: NotificationMode


def get_notification(session):
    message = session["notification-message"]
    raw_mode = session["notification-mode"]
    try:
        mode = NotificationMode(raw_mode)
    except ValueError:
        raise UnknownOptionError(
            f"'{raw_mode}' is not a valid notification mode."
        )
    return Notification(message=message, mode=mode)


def set_notification(session, notification):
    session["notification-message"] = notification.message
    session["notification-mode"] = notification.mode.value


def reset_notifications(session):
    notification = Notification(message="", mode=NotificationMode.NONE)
    set_notification(session, notification)


def init_notifications(session):
    reset_notifications(session)


def render_notifications(session, show):
    notification = get_notification(session)
    return render_template(
        "partials/notification_banner.html",
        modes=get_modes_str(session),
        message=notification.message,
        mode=notification.mode.value,
        show=show,
    )
