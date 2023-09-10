def kwargs_pop_item(kwargs, key, default_value):
    if key in kwargs:
        value = kwargs[key]
        del kwargs[key]
    else:
        value = default_value
    return value


def kwargs_push_item(kwargs, key, value):
    kwargs[key] = value
