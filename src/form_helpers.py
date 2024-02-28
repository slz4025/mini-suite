import src.errors as errors


def extract(form, key, name=None):
    if name is None:
        name = key
    if key not in form:
        raise errors.UserError(
            f"Field '{name}' was not given."
        )
    return form[key]


def parse_int(s, name):
    try:
        return int(s)
    except ValueError:
        raise errors.UserError(
            f"Field '{name}' with value '{s}' is not integer."
        )


def validate_nonempty(value, name):
    if value == "":
        raise errors.UserError(
            f"Field '{name}' was not given."
        )
