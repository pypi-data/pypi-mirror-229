from typing import Callable, Type, TypeVar

T = TypeVar('T')

observer_stores = []


def observer(name: str) -> Callable[[Type[T]], Type[T]]:
    def decorator(cls: Type[T]) -> Type[T]:
        observer_stores.append(cls)
        setattr(cls, '__observer_name', name)
        return cls

    return decorator
