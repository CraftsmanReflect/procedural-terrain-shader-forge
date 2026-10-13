"""Minimal synchronous pub/sub. Handlers run on the publishing thread."""
from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any

_LOG = logging.getLogger(__name__)

Handler = Callable[..., None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._handlers[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Handler) -> None:
        try:
            self._handlers[topic].remove(handler)
        except (KeyError, ValueError):
            pass

    def publish(self, topic: str, **payload: Any) -> None:
        for handler in list(self._handlers.get(topic, ())):
            try:
                handler(**payload)
            except Exception:
                _LOG.exception("event handler failed on topic %s", topic)