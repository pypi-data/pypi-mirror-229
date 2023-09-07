import inspect
import re
from typing import Any, Callable

from fastapi import Depends

from ..helpers.dependency import observer_dependencies
from ..services.event_emitter import EventEmitterService


class EventHandlerService:
    def __init__(
        self,
        observers=Depends(observer_dependencies()),
        event: EventEmitterService = Depends(),
    ):
        self.observers = observers
        event.handler = self.emit

    async def emit(self, name: str, data: Any):
        for observer in self.get_observers(name):
            functions = self.get_functions(name, observer)
            for function in functions:
                await function(data)

    def get_observers(self, name: str):
        match_observers = []

        for observer in self.observers:
            observer_name: str = getattr(observer, '__observer_name')
            if re.search(observer_name, name) is not None:
                match_observers.append(observer)

        return match_observers

    def get_functions(self, name: str, observer: Callable):
        functions = []
        for member in inspect.getmembers(observer):
            function = getattr(observer, member[0])
            if hasattr(function, '__event_name'):
                event_handle_name = getattr(function, '__event_name')
                if event_handle_name in ['*', name]:
                    functions.append(function)

        return functions
