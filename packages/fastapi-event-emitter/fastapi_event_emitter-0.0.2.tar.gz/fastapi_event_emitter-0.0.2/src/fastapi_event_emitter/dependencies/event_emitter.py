from fastapi import Depends

from ..services.event_emitter import EventEmitterService
from ..services.event_handler import EventHandlerService


def event_emitter_depends(
    event_emitter_service: EventEmitterService = Depends(),
    event_handler_service: EventHandlerService = Depends(),  # noqa
):
    return event_emitter_service


def get_event_emitter() -> EventEmitterService:
    return Depends(event_emitter_depends)
