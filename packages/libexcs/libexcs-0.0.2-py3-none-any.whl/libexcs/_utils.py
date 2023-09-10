import typing as t


def format_kwargs(**kwargs: t.Any):
    return ", ".join(f"{k!s}={v!r}" for k, v in kwargs.items())
