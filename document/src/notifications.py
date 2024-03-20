from dataclasses import dataclass
from enum import Enum
from flask import render_template


class Mode(Enum):
    NONE = "none"
    INFO = "info"
    WARN = "warning"
    ERROR = "error"


@dataclass
class Notification:
    message: str
    mode: Mode


notification = None


def get():
    return notification


def set(note):
    global notification
    notification = note


def reset():
    global notification
    notification = Notification(message="", mode=Mode.NONE)


def init():
    reset()


def set_error(error):
    set(Notification(message=str(error), mode=Mode.ERROR))


def set_info(message):
    set(Notification(message=message, mode=Mode.INFO))


def render(session):
    notification = get()
    show = notification.mode != Mode.NONE
    return render_template(
        "partials/notification_banner.html",
        message=notification.message,
        mode=notification.mode.value,
        show=show,
    )
