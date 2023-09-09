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

"""Provides generic machinery to spawn a bunch of local or remote monitoring processes in a
minimon application context
"""

import asyncio
import functools
import logging
import shlex
import sys
from asyncio import StreamReader
from asyncio.subprocess import PIPE, create_subprocess_exec
from collections.abc import AsyncIterator, Callable, Sequence
from dataclasses import dataclass
from itertools import count
from typing import Any

import asyncssh

from minimon.machinery import Pipeline, StrSeq, bundle
from minimon.server import Context, Insight, Insights, Singleton, serve

__all__ = [
    "Monitor",
    "GlobalMonitorContext",
    "Pipeline",
    "Host",
    "Hosts",
    "Insight",
    "Insights",
    "StrSeq",
    "view",
    "process_output",
    "bundle",
]


def log() -> logging.Logger:
    """Logger for this module"""
    return logging.getLogger("minimon")


class GlobalMonitorContext(Context, metaclass=Singleton):
    """A singleton minimon application context"""


@dataclass
class Host:
    """Specification of a remote host with everything needed to establish an SSH connection"""

    name: str
    ip_address: None | str = None
    ssh_name: None | str = None
    ssh_key_file: None | str = None
    ssh_key_passphrase_cmd: None | str = None
    ssh_port: None | int = None

    def __str__(self) -> str:
        return self.name


Hosts = Sequence[Host]

# https://realpython.com/primer-on-python-decorators/#syntactic-sugar
def view(
    arg_name: str, arg_values: Sequence[object]
) -> Callable[[Callable[[object], AsyncIterator[Insight]]], None]:
    """A decorator generating a minimon view for each value in @arg_values"""

    def decorator_view(afunc: Callable[[object], AsyncIterator[Insight]]) -> None:
        @functools.wraps(afunc)
        async def wrapper_view(*args: object, **kwargs: object) -> AsyncIterator[Insight]:
            generator = afunc(*args, **kwargs)
            while True:
                try:
                    yield await anext(generator)
                except StopAsyncIteration:
                    log().info("StopAsyncIteration in %s", afunc.__name__)
                    break
                except Exception:  # pylint: disable=broad-except
                    log().exception("Unhandled exception in view generator:")

        fn_name = afunc.__name__
        for arg_value in arg_values:
            GlobalMonitorContext().add(
                f"{fn_name}-{arg_value}", wrapper_view(**{arg_name: arg_value})
            )

    return decorator_view


class HostConnection:
    """An SSH connection to a given @host"""

    def __init__(self, host: Host, log_fn: Callable[[str], None]) -> None:
        self.host_info = host
        self.log_fn = log_fn
        self.ssh_connection: None | asyncssh.SSHClientConnection = None

    async def __aenter__(self) -> "HostConnection":
        if self.host_info.ssh_name:
            try:
                self.ssh_connection = await asyncssh.connect(
                    self.host_info.ip_address or self.host_info.name,
                    port=self.host_info.ssh_port or (),
                    username=self.host_info.ssh_name,
                    # client_keys=[pkey],
                )
            except asyncssh.HostKeyNotVerifiable as exc:
                raise RuntimeError(f"Cannot connect to {self.host_info.name}: {exc}") from exc

        return self

    async def __aexit__(self, *args: object) -> bool:
        if self.ssh_connection:
            self.ssh_connection.close()
        return True

    @staticmethod
    def clean_lines(raw_line: str, log_fn: Callable[[str], None]) -> str:
        """Sanatize and log a str line"""
        line = raw_line.strip("\n")
        log_fn(line)
        return line

    @staticmethod
    def clean_bytes(raw_line: bytes, log_fn: Callable[[str], None]) -> str:
        """Sanatize and log a bytes line"""
        line = raw_line.decode().strip("\n")
        log_fn(line)
        return line

    async def listen(
        self,
        stream: StreamReader | asyncssh.SSHReader[Any],
        clean_fn: Callable[[bytes, Callable[[str], None]], str]
        | Callable[[str, Callable[[str], None]], str],
    ) -> Sequence[str]:
        """Creates a sanatized list of strings from something iterable and logs on the go"""
        return [clean_fn(raw_line, self.log_fn) async for raw_line in aiter(stream)]

    async def execute(self, command: str) -> tuple[Sequence[str], Sequence[str], int]:
        """Executes @command via ssh connection if specified else locally"""
        if self.ssh_connection:

            ssh_process = await self.ssh_connection.create_process(command)
            assert ssh_process.stdout and ssh_process.stderr
            stdout, stderr, completed = await asyncio.gather(
                self.listen(ssh_process.stdout, self.clean_lines),
                self.listen(ssh_process.stderr, self.clean_lines),
                asyncio.ensure_future(ssh_process.wait()),
            )
            assert completed.returncode is not None
            return stdout, stderr, completed.returncode

        process = await create_subprocess_exec(*shlex.split(command), stdout=PIPE, stderr=PIPE)
        assert process.stdout and process.stderr
        return await asyncio.gather(
            self.listen(process.stdout, self.clean_bytes),
            self.listen(process.stderr, self.clean_bytes),
            process.wait(),
        )


async def process_output(
    host: Host,
    command: str,
    when: None | str = None,
) -> AsyncIterator[Sequence[str]]:
    """Executes a process defined by @command on @host in a manner specified by @when"""
    iterations = None
    interval = float(when) if when is not None else None

    async with HostConnection(host, GlobalMonitorContext().ctx_log_fn()) as connection:
        for iteration in count():
            if iterations is not None and iteration >= iterations:
                break

            log().info("start task %r: %d", command, iteration)
            try:
                stdout, _, return_code = await connection.execute(command)
                log().info("task %r: %d, returned %d", command, iteration, return_code)
                yield stdout
            except Exception:  # pylint: disable=broad-except
                log().exception("Executing command %s resulted in unhandled exception")

            if interval is not None:
                await asyncio.sleep(interval)


class Monitor:
    """Top level application context, instantiating the monitoring application"""

    def __init__(self, name: str, log_level: str = "INFO") -> None:
        self.name = name
        self.log_level = log_level

    def __enter__(self) -> "Monitor":
        return self

    def __exit__(self, *args: object) -> bool:
        if sys.exc_info() != (None, None, None):
            raise

        serve(GlobalMonitorContext(), self.log_level)
        return True


# with suppress(FileNotFoundError):
# with open(CONFIG_FILE) as config_file:
# config = yaml.load(config_file, yaml.Loader)
# print(config)
