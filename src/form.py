def extract(form, key, name=None):
    if name is None:
        name = key
    if key not in form:
        raise Exception(f"Field '{name}' was not given.")
    return form[key]


def parse_int(s, name):
    try:
        return int(s)
    except ValueError:
        raise Exception(f"Field '{name}' with value '{s}' is not integer.")


def validate_bounds(num, min_bound, max_bound, name):
    if num < min_bound:
        raise Exception(
            f"Field '{name}' with value {num} "
            f"is lower than min bound, {min_bound}."
        )
    if num >= max_bound:
        raise Exception(
            f"Field '{name}' with value {num} "
            f"is not within max bound, {max_bound}."
        )


def validate_nonempty(value, name):
    if value == "":
        raise Exception(f"Field '{name}' was not given.")
