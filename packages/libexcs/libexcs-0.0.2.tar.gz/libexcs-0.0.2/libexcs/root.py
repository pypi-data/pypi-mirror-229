import typing as t

from libexcs import _utils


class RootException(Exception):
    _template_ = "Unknown exception (root)"

    def __init__(self, **kwargs: t.Any) -> None:
        self.__kwargs = kwargs
        try:
            self.__msg = self._template_.format(**self.__kwargs)
        except Exception as e:
            raise TypeError(f"Not enough arguments: {e}")
        for k, v in self.__kwargs.items():
            setattr(self, k, v)
        super().__init__(self.__msg)

    def __repr__(self) -> str:
        kwargs = _utils.format_kwargs(**self.__kwargs)
        return f"{type(self).__name__}({kwargs})"

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.__msg}"
