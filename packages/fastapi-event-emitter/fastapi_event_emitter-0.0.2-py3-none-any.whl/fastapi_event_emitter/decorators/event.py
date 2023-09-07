from typing import Callable, Type, TypeVar

T = TypeVar('T')


def event(name: str) -> Callable[[Type[T]], Type[T]]:
    def decorator(cls: Type[T]) -> Type[T]:
        setattr(cls, '__event_name', name)
        return cls

    return decorator
