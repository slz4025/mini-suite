import copy


buffer = None


def get_buffer():
    if buffer is None:
        return buffer

    # Copy objects, e.g. strings, within the array.
    copied_buffer = copy.deepcopy(buffer)
    return copied_buffer


def set_buffer(buf):
    # Assume buf is pointer to desired data.
    # Copy objects, e.g. strings, within the array.
    copied_buf = copy.deepcopy(buf)

    global buffer
    buffer = copied_buf
