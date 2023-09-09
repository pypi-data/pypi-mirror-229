#!/usr/bin/env python3
# pylint: disable=wildcard-import,unused-wildcard-import

""" Monitor Checkmk CI
build-fra*
 - docker
   - total cpu / ram
   - number of containers
   - per container
       - start / stop
       - cpu / ram
       - volumes
       - associated jenkins job
       -
   - number of images
   - number of volumes

agentbuild?

jenkins
   - job tree
   - warning about certain job results
   - branch sheriffing state

nexus
   - free space
   - artifacts overview

actions
 - rebuild failed jobs
 - kill/delete containers/volumes/tags/images
 - open/close branches
 - cleanup workspace(s)

reactions
 - send build break notifications
 - later: open/close branches
"""

from minimon.builder import (
    Host,
    Insights,
    Monitor,
    Pipeline,
    bundle,
    process_output,
    view,
)
from minimon.plugins import parse_df, parse_dmesg, parse_du

hosts = (
    Host("localhost", ssh_name="root"),
    Host("build-fra-001", ssh_name="root"),
    Host("build-fra-002", ssh_name="root"),
    Host("build-fra-003", ssh_name="root"),
    Host("ci", ssh_name="root"),
    Host("review", ssh_name="root"),
    Host("artifacts", ssh_name="root"),
    Host("bazel-cache", ssh_name="root"),
    Host("tstbuilds-artifacts", ssh_name="root"),
    # Host("devpi", ssh_name="root"),
)

with Monitor("ci_dashboard"):

    @view("host", hosts)  # type: ignore[arg-type]
    async def local_resources(host: Host) -> Insights:
        """View for local resources"""
        state = {}
        async for name, lines in bundle(
            ps=Pipeline(process_output(host, "ps wauxw", "1"), processor=parse_du),
            df=Pipeline(process_output(host, "df -P", "2"), processor=parse_df),
            dmesg=Pipeline(process_output(host, "dmesg", "2"), processor=parse_dmesg),
        ):
            state[name] = lines
            yield state
