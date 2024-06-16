from flask import render_template

import src.notifications.state as state
import src.notifications.types as types


def render():
    id = state.get_id()
    mode, message = state.get_notification()

    match (mode):
        case types.Mode.NONE:
            icon = "😌"
        case types.Mode.INFO:
            icon = "😀"
        case types.Mode.WARN:
            icon = "😮"
        case types.Mode.ERROR:
            icon = "😦"

    return render_template(
        "partials/notification_banner.html",
        icon=icon,
        message=message,
        mode=mode.value,
        id=id,
    )
