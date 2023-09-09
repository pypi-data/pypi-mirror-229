from __future__ import annotations

from datetime import timedelta
from typing import *  # type: ignore

import fastapi


__all__ = [
    "App",
]


class App:
    def __init__(
        self,
        name: str,
        build: Any,  # TODO
        *,
        default_attachments: Iterable[Any] = (),
        ping_pong_interval: Union[int, float, timedelta] = timedelta(seconds=50),
    ):
        self.name = name
        self.build = build
        self.default_attachments = tuple(default_attachments)

        if isinstance(ping_pong_interval, timedelta):
            self.ping_pong_interval = ping_pong_interval
        else:
            self.ping_pong_interval = timedelta(seconds=ping_pong_interval)

    def as_fastapi(
        self,
        external_url: str,
    ) -> fastapi.FastAPI:
        raise NotImplementedError("TODO: Run as fastapi")
