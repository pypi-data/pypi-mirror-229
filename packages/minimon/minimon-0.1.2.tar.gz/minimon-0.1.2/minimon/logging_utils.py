#!/usr/bin/env python3
#            _       _
#  _ __ ___ (_)_ __ (_)_ __ ___   ___  _ __
# | '_ ` _ \| | '_ \| | '_ ` _ \ / _ \| '_ \
# | | | | | | | | | | | | | | | | (_) | | | |
# |_| |_| |_|_|_| |_|_|_| |_| |_|\___/|_| |_|
#
# minimon - a minimal monitor
# Copyright (C) 2023 - Frans Fürst
#
# minimon is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# minimon is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details at <http://www.gnu.org/licenses/>.
#
# Anyway this project is not free for machine learning. If you're using any content of this
# repository to train any sort of machine learned model (e.g. LLMs), you agree to make the whole
# model trained with this repository and all data needed to train (i.e. reproduce) the model
# publicly and freely available (i.e. free of charge and with no obligation to register to any
# service) and make sure to inform the author (me, frans.fuerst@protonmail.com) via email how to
# get and use that model and any sources needed to train it.

"""Common stuff shared among modules"""

import logging
import sys
import threading
import traceback
from collections.abc import Iterator, Mapping
from types import TracebackType

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def log() -> logging.Logger:
    """Logger for this module"""
    return logging.getLogger("minimon")


def stack_str(depth: int = 0) -> str:
    """Create a tiny string from current call stack"""

    def stack_fns() -> Iterator[str]:
        # pylint: disable=protected-access
        stack = list(reversed(traceback.extract_stack(sys._getframe(depth))))
        for site in stack:
            if site.filename != stack[0].filename or site.name == "<module>":
                break
            yield site.name

    return ">".join(reversed(list(stack_fns())))


def setup_logging(level: str = "INFO") -> None:
    """Make logging fun"""

    class CustomLogger(logging.Logger):
        """Logs a record the way we want it"""

        # pylint: disable=too-many-arguments
        def makeRecord(
            self,
            name: str,
            level: int,
            fn: str,
            lno: int,
            msg: object,
            args: tuple[object, ...] | Mapping[str, object],
            exc_info: tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | None,
            func: str | None = None,
            extra: Mapping[str, object] | None = None,
            sinfo: str | None = None,
        ) -> logging.LogRecord:
            """Creates a log record with a 'stack' element"""
            new_extra = {
                **(extra or {}),
                **{
                    "stack": stack_str(5),
                    "posixTID": threading.get_native_id(),
                },
            }
            return super().makeRecord(
                name, level, fn, lno, msg, args, exc_info, func, new_extra, sinfo
            )

    # for lev in LOG_LEVELS:
    #    logging.addLevelName(getattr(logging, lev), f"{lev[0] * 2}")

    logging.setLoggerClass(CustomLogger)

    log().setLevel(getattr(logging, level.split("_")[-1]))
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(getattr(logging, level.split("_")[-1]))
    stream_handler.setFormatter(
        logging.Formatter(
            "(%(levelname)s) %(asctime)s | %(posixTID)d | %(stack)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    log().handlers = [stream_handler]
    logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)

    # https://stackoverflow.com/questions/76788727/how-can-i-change-the-debug-level-and-format-for-the-quart-i-e-hypercorn-logge
    # https://pgjones.gitlab.io/hypercorn/how_to_guides/logging.html#how-to-log
    # https://www.phind.com/agent?cache=clkqhh48y001smg0832tvq1rl

    # from quart.logging import default_handler
    # logging.getLogger('quart.app').removeHandler(default_handler)
    # logger = logging.getLogger("hypercorn.error")
    # logger.removeHandler(default_handler)
    # logger.addHandler(ch)
    # logger.setLevel(logging.WARNING)
    # logger.propagate = False
