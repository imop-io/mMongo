# coding: utf8


def to_snake_case(camel_case):
    return (
        ''.join([
            "_" + x.lower()
            if i < (len(camel_case) - 1) and x.isupper() and camel_case[i + 1].islower()  # noqa
            else x.lower() + "_"
            if i < (len(camel_case) - 1) and x.islower() and camel_case[i + 1].isupper()  # noqa
            else x.lower() for i, x in enumerate(list(camel_case))])
    ) \
        .lstrip('_') \
        .replace('__', '_') \
        + 's'
