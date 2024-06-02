from flask import (
    make_response,
    url_for,
)
import traceback

import src.errors.types as types
import src.errors.state as state


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
            state.set_message(error_message)

            # Print error in case can't redirect to page.
            # Seems like this usually happens when an unexpected bug
            # is encountered.
            print(error_message)

            resp = make_response()
            resp.headers["HX-Redirect"] = url_for("render_error")

        return resp

    # Register each wrapper for each endpoint under a different name.
    wrapper.__name__ = func.__name__ + "__error_handler"
    return wrapper
