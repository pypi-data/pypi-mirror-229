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

""" Function plumbing stuff
"""

import asyncio
import logging
from collections.abc import AsyncIterator, Callable, Iterator, MutableSequence, Sequence
from contextlib import suppress
from pathlib import Path
from typing import Any, TypeAlias, TypeVar, Union, cast

from asyncinotify import Inotify, Mask

StrSeq: TypeAlias = Sequence[str]


def log() -> logging.Logger:
    """Logger for this module"""
    return logging.getLogger("minimon")


T = TypeVar("T")


class Pipeline(AsyncIterator[T]):
    """Data emitter used for plumbing"""

    def __init__(
        self,
        source: Union["Pipeline[T]", AsyncIterator[Any]],
        processor: None | Callable[[Any], T] = None,
        name: None | str = None,
        terminal: bool = False,
    ):
        self._subscribers: MutableSequence[asyncio.Queue[T]] = []
        self.name = name
        self.terminal = terminal

        self._aiter = self._aemit(
            self._alisten(source.subscribe()) if isinstance(source, Pipeline) else source, processor
        ).__aiter__()

    @staticmethod
    async def _alisten(queue: asyncio.Queue[T]) -> AsyncIterator[T]:
        while True:
            yield await queue.get()

    async def _aemit(
        self,
        source: AsyncIterator[Any],
        processor: None | Callable[[Any], T],
    ) -> AsyncIterator[T]:
        """"""
        async for value in source:
            final_value = processor(value) if processor else cast(T, value)
            yield final_value
            for subscriber in self._subscribers:
                await subscriber.put(final_value)

    def __aiter__(self) -> AsyncIterator[T]:
        """Returns the previously created iterator"""
        return self._aiter

    async def __anext__(self) -> T:
        """Returns the previously created iterator"""
        return await anext(self._aiter)

    def subscribe(self) -> asyncio.Queue[T]:
        """Creates, registeres and returns a new queue for message publishing"""
        queue: asyncio.Queue[T] = asyncio.Queue()
        self._subscribers.append(queue)
        return queue


async def bundle(**generators: AsyncIterator[T]) -> AsyncIterator[tuple[str, T]]:
    """Iterates over provided async generators combined"""

    async def result_with_gen(gen: AsyncIterator[T]) -> AsyncIterator[tuple[AsyncIterator[T], T]]:
        """Yields results from @gen together with @gen"""
        async for result in gen:
            yield gen, result

    def task_from(name: str, gen: AsyncIterator[T]) -> asyncio.Task[T]:
        """Returns a named task retrieving the next element of @gen"""
        return asyncio.create_task(anext(result_with_gen(gen)), name=name)  # type: ignore[arg-type]

    tasks = set(task_from(name, gen) for name, gen in dict(generators).items())

    while tasks:
        done, tasks = await asyncio.wait(fs=tasks, return_when=asyncio.FIRST_COMPLETED)
        for event in done:
            with suppress(StopAsyncIteration):
                gen, result = cast(tuple[AsyncIterator[T], T], event.result())
                name = event.get_name()
                tasks.add(task_from(name, gen))
                yield name, result


async def throttle(
    generator: AsyncIterator[T],
    postpone: bool = False,
    min_interval: float = 2,
) -> AsyncIterator[Sequence[T]]:
    """Read events from @generator and return in bundled chunks only after @min_interval seconds
    have passed
    """

    async def add_next(
        gen: AsyncIterator[T], elements: MutableSequence[T], abort: asyncio.Event
    ) -> None:
        """Wrapper for anext() firing an event on StopAsyncIteration"""
        with suppress(StopAsyncIteration):
            elements.append(await anext(gen))
            return
        abort.set()

    fuse_task = None
    abort = asyncio.Event()
    collected_events: MutableSequence[T] = []
    tasks = {
        asyncio.create_task(abort.wait(), name="abort"),
        asyncio.create_task(add_next(generator, collected_events, abort), name="nextelem"),
    }

    while True:
        done, tasks = await asyncio.wait(fs=tasks, return_when=asyncio.FIRST_COMPLETED)

        for event in done:
            if event.get_name() in {"fuse", "abort"}:
                del fuse_task
                fuse_task = None
                yield collected_events
                collected_events.clear()
                if event.get_name() == "abort":
                    for task in tasks:
                        task.cancel()
                    return
                continue

            # in case we're postponing we 'reset' the timeout fuse by removing it
            if postpone and fuse_task:
                tasks.remove(fuse_task)
                fuse_task.cancel()
                del fuse_task
                fuse_task = None

            # we've had a new event - start the timeout fuse
            if not fuse_task:
                tasks.add(
                    fuse_task := asyncio.create_task(asyncio.sleep(min_interval), name="fuse")
                )

            tasks.add(
                asyncio.create_task(add_next(generator, collected_events, abort), name="nextelem")
            )


async def fs_changes(
    *paths: Path,
    mask: Mask = Mask.CLOSE_WRITE
    | Mask.MOVED_TO
    | Mask.CREATE
    | Mask.MODIFY
    | Mask.MOVE
    | Mask.DELETE
    | Mask.MOVE_SELF,
) -> AsyncIterator[Path]:
    """Controllable, timed filesystem watcher"""

    def expand_paths(path: Path, recursive: bool = True) -> Iterator[Path]:
        yield path
        if path.is_dir() and recursive:
            for file_or_directory in path.rglob("*"):
                if file_or_directory.is_dir() and all(
                    p not in file_or_directory.absolute().as_posix()
                    for p in (
                        "/.venv",
                        "/.git",
                        "/.mypy_cache",
                        "/dist",
                        "/__pycache__",
                    )
                ):
                    yield file_or_directory

    with Inotify() as inotify:
        for path in set(sub_path.absolute() for p in paths for sub_path in expand_paths(Path(p))):
            log().debug("add fs watch for %s", path)
            inotify.add_watch(path, mask)

        async for event_value in inotify:
            if event_value.path:
                yield event_value.path
