from typing import Any, Callable, Optional


class EventEmitterService:
    def __init__(self):
        self.handler: Optional[Callable] = None

    async def emit(self, name: str, data: Any):
        if self.handler is not None:
            await self.handler(name, data)
