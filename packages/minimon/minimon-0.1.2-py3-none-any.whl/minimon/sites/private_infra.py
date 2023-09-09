#!/usr/bin/env python3
# pylint: disable=wildcard-import,unused-wildcard-import

""" Monitor my private infrastructure
Todo
- wth: monitor networks
"""

from minimon.builder import (
    Host,
    Insights,
    Monitor,
    Pipeline,
    StrSeq,
    bundle,
    process_output,
    view,
)
from minimon.plugins import parse_df, parse_dmesg, parse_du, parse_ss

hosts = (
    # Host("localhost"),
    Host("localhost", ssh_name="root"),
    # Host("om-office.de", ssh_name="frans", ssh_port=2222),
    # Host("zentrale", ssh_name="frans"),
    # Host("remarkable", ssh_name="frans"),
    # Host("handy", ssh_name="frans"),
)

with Monitor("Private inf"):

    @view("host", hosts)  # type: ignore[arg-type]
    async def network_traffic(host: Host) -> Insights:
        """Provides quick summary of system sanity"""
        async for _ in Pipeline[StrSeq](
            process_output(host, "ss --oneline --numeric --resolve --processes --info", "3"),
            processor=parse_ss,
        ):
            yield {}

    @view("host", hosts)  # type: ignore[arg-type]
    async def local_resources(host: Host) -> Insights:
        """Provides quick summary of system sanity"""
        state = {}
        async for name, lines in bundle(
            ps=Pipeline(process_output(host, "ps wauxw", "1"), processor=parse_du),
            df=Pipeline(process_output(host, "df -P", "2"), processor=parse_df),
            dmesg=Pipeline(process_output(host, "dmesg", "2"), processor=parse_dmesg),
        ):
            state[name] = lines
            yield state
