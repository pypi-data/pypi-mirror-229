import inspect
from typing import Callable

from fastapi import Depends

from ..decorators.observer import observer_stores


def observer_dependencies() -> Callable:
    def merged_dependencies(**kwargs):
        return list(kwargs.values())

    merged_dependencies.__signature__ = inspect.Signature(  # type: ignore
        parameters=[
            inspect.Parameter(f"dep{key}", inspect.Parameter.KEYWORD_ONLY, default=Depends(dep))
            for key, dep in enumerate(observer_stores)
        ]
    )
    return merged_dependencies
