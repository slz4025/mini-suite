import src.errors.types as err_types


def extract(form, key, name=None):
    if name is None:
        name = key
    if key not in form:
        raise err_types.InputError(
            f"Field '{name}' was not given."
        )
    return form[key]


def parse_int(s, name):
    try:
        return int(s)
    except ValueError:
        raise err_types.InputError(
            f"Field '{name}' with value '{s}' is not integer."
        )


def validate_nonempty(value, name):
    if value == "":
        raise err_types.InputError(
            f"Field '{name}' was not given."
        )
