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

"""The core stuff"""

import asyncio
import logging
import signal
import threading
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping, MutableMapping
from contextvars import ContextVar

from rich.logging import RichHandler
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import Footer, Header, Log, Pretty, RichLog, Static

from minimon.logging_utils import setup_logging

Insight = Mapping[str, object]
Insights = AsyncIterator[Insight]


def log() -> logging.Logger:
    """Logger for this module"""
    return logging.getLogger("minimon")


class Context:
    """A minimon application context - too fuzzy to describe for now"""

    def __init__(self) -> None:
        self.things: MutableMapping[str, AsyncIterator[Insight]] = {}
        self.log_widgets: MutableMapping[str, Callable[[str], None]] = {}
        self.logger_context: ContextVar[str] = ContextVar("logger_context")

    def add(self, name: str, generator: AsyncIterator[Insight]) -> None:
        """Registeres a view's generator"""
        self.things[name] = generator

    def ctx_log_fn(self) -> Callable[[str], None]:
        """Returns the UI logging function for the current async context"""
        try:
            return self.log_widgets[self.logger_context.get()]
        except LookupError:
            return lambda raw_line: None if not (line := raw_line.rstrip()) else print(f":| {line}")

    def set_current_logger(self, name: str, log_widget: Log) -> None:
        """Configures the logging function for the async context called from"""
        self.logger_context.set(name)
        self.log_widgets[name] = lambda raw_line: (
            None
            if not (line := raw_line.rstrip())
            else None
            if log_widget.write_line(line)
            else None
        )


class RichLogHandler(RichHandler):
    """Redirects rich.RichHanlder capabilities to a textual.RichLog"""

    def __init__(self, widget: RichLog, error_widget: RichLog):
        super().__init__(
            # show_time = False,
            # omit_repeated_times = False,
            # show_level = False,
            show_path=False,
            # enable_link_path = False,
            markup=False,
            # rich_tracebacks = False,
            # tracebacks_width: Optional[int] = None,
            # tracebacks_extra_lines: int = 3,
            # tracebacks_theme: Optional[str] = None,
            # tracebacks_word_wrap: bool = True,
            # tracebacks_show_locals: bool = False,
            # tracebacks_suppress: Iterable[Union[str, ModuleType]] = (),
            # locals_max_length: int = 10,
            # locals_max_string: int = 80,
            # log_time_format = "[%x %X]",
            # keywords= None,
        )
        self.widget: RichLog = widget
        self.error_widget: RichLog = error_widget

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        message_renderable = self.render_message(record, message)
        traceback = None
        log_renderable = self.render(
            record=record, traceback=traceback, message_renderable=message_renderable
        )
        self.widget.write(log_renderable)
        if record.levelname not in {"DEBUG", "INFO", "WARNING"}:
            self.error_widget.write(log_renderable)


class TaskWidget(Static):
    """Generic widget for task visualization"""

    def compose(self) -> ComposeResult:
        yield Pretty({}, classes="box")
        yield Log(classes="box")


class MiniMoni(App[None]):
    """Terminal monitor for minimon"""

    CSS_PATH = "minimon.css"
    TITLE = "minimon"

    def __init__(self, context: Context) -> None:
        super().__init__()
        self._widget_container = VerticalScroll()
        self._normal_log = RichLog()
        self._normal_log.border_title = "messages"
        self._error_log = RichLog()
        self._error_log.border_title = "errors"
        self.context = context

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield self._widget_container
        with Horizontal():
            yield self._normal_log
            yield self._error_log

    @staticmethod
    async def _handle_monitoring_info(  # pylint: disable=too-many-arguments
        name: str,
        task_fn: AsyncIterator[Insight],
        context: Context,
        widget: TaskWidget,
        update: Callable[[Insight], None],
        cleanup: Callable[[], Awaitable[None]],
    ) -> None:
        """Reads from provided generator and updates corresponding widget"""
        try:
            log().info("task %r started", task_fn)
            context.set_current_logger(name, widget.query_one(Log))
            async for data in task_fn:
                update(data)

        except Exception:  # pylint: disable=broad-except
            log().exception("exception in %r", task_fn)
        finally:
            log().info("task %r terminated", task_fn)
            await cleanup()

    async def create_widget(self, title: str) -> TaskWidget:
        """Creates, configures and returns a TaskWidget"""
        await self._widget_container.mount(widget := TaskWidget())
        widget.border_title = title
        return widget

    async def remove_widget(self, widget: TaskWidget) -> None:
        """Asynchronously removes given @widget"""
        await widget.remove()

    async def add_task(self, name: str, task: AsyncIterator[Insight]) -> TaskWidget:
        """Registers a new process task to be executed"""
        widget = await self.create_widget(name)
        pretty: Pretty = widget.query_one(Pretty)
        asyncio.ensure_future(
            self._handle_monitoring_info(
                name,
                task,
                self.context,
                widget,
                pretty.update,
                lambda: self.remove_widget(widget),
            )
        )
        return widget

    async def on_mount(self) -> None:
        """UI entry point"""

        log().handlers = [RichLogHandler(self._normal_log, self._error_log)]

        for name, generator in self.context.things.items():
            await self.add_task(name, generator)

    @on(Message)
    async def on_msg(self, *event: str) -> None:
        """Generic message handler"""
        # log().debug("Event: %s", event)

    async def exe(self, on_exit: Callable[[], None]) -> None:
        """Execute and quit application"""
        try:
            await self.run_async()
        finally:
            on_exit()


def terminate(terminator: threading.Event) -> None:
    """Sends a signal to async tasks to tell them to stop"""
    try:
        terminator.set()
        for task in asyncio.all_tasks():
            task.cancel()
        asyncio.get_event_loop().stop()
    except Exception:  # pylint: disable=broad-except
        log().exception("terminate:")


def install_signal_handler(loop: asyncio.AbstractEventLoop, on_signal: Callable[[], None]) -> None:
    """Installs the CTRL+C application termination signal handler"""
    for signal_enum in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(signal_enum, on_signal)


class Singleton(type):
    """Yes, a Singleton"""

    _instances: MutableMapping[type, object] = {}

    def __call__(cls: "Singleton", *args: object, **kwargs: object) -> object:
        """Creates an instance if not available yet, returns it"""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def serve(context: Context, log_level: str = "INFO") -> int:
    """Synchronous entry point"""
    setup_logging(log_level)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    terminator = threading.Event()

    asyncio.ensure_future(MiniMoni(context).exe(lambda: terminate(terminator)))

    try:
        install_signal_handler(loop, lambda: terminate(terminator))
        log().info("CTRL+C to quit")
        loop.run_forever()
    finally:
        log().debug("finally - loop.run_forever()")

    return 0
