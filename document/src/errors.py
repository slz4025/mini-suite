from flask import (
        session,
        make_response,
        url_for,
        )
import traceback


# Errors that arise due to general bad user input/action.
class UserError(Exception):
    pass


def get_message(session):
    if "error-message" not in session:
        return None
    return session["error-message"]


def set_message(session, error_message):
    session["error-message"] = error_message


def handler(func):
    def wrapper(*args, **kwargs):
        resp = None

        error = None

        try:
            resp = func(*args, **kwargs)
        except Exception as e:
            error = e

        if error is not None:
            stack_trace = "".join(traceback.format_tb(error.__traceback__))
            error_message = f"ERROR: {error}\n{stack_trace}"
            set_message(session, error_message)

            # Print error in case can't redirect to page.
            # Seems like this usually happens when an unexpected bug
            # is encountered.
            print(error_message)

            resp = make_response()
            resp.headers["HX-Redirect"] = url_for("unexpected_error")

        return resp

    # Register each wrapper for each endpoint under a different name.
    wrapper.__name__ = func.__name__ + "__error_handler"
    return wrapper
