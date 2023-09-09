#!/usr/bin/env python3
# pylint: disable=wildcard-import,unused-wildcard-import

""" A minimal viable monitor"""

from minimon import *
from minimon.plugins import *

with Monitor("MVM"):

    @view("host", [Host("localhost")])  # type: ignore[arg-type]
    async def local_resources(host: Host) -> Insights:
        """This async generator will be invoked by the above `view` and run continuously to
        gather and yield monitoring data"""
        current_insights = {}
        async for name, lines in bundle(
            ps=Pipeline(process_output(host, "ps wauxw", "1"), processor=parse_du),
            df=Pipeline(process_output(host, "df -P", "2"), processor=parse_df),
            dmesg=Pipeline(process_output(host, "dmesg", "2"), processor=parse_dmesg),
        ):
            current_insights[name] = lines
            yield current_insights
