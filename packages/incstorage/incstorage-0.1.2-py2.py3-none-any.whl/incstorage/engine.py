import asyncio
import sys
import traceback

from typing import List

from .agent import Agent

# ----------------------------------------------------------
# loggers
# ----------------------------------------------------------
from pycelium.tools.logs import logger

log = logger(__name__)

# ----------------------------------------------------------
# Engine
# ----------------------------------------------------------

from async_timeout import timeout


class Engine:
    """TBD"""

    nodes: List[Agent]

    def __init__(self, agents: List[Agent] = []):
        self.agents = agents
        self.running = False

    def add(self, *agents):
        assert all([isinstance(obj, Agent) for obj in agents] or [True])
        self.agents.extend(agents)

    async def main(
        self,
        since=None,
        max_records=sys.float_info.max,
        max_run=sys.float_info.max,
    ):
        self.running = True

        # setup input streams
        if max_records <= 0:
            return

        # loop
        try:
            async with timeout(max_run) as to:
                async with asyncio.TaskGroup() as group:
                    for node in self.agents:
                        log.debug(f"starting agent: {node}")
                        group.create_task(node.main())

                    while self.running:
                        await asyncio.sleep(1)
                        if not self.running or max_records <= 0:
                            break
                    to.update(0)  # force break
        except TimeoutError as why:
            pass

        except Exception as why:
            print(why)
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)

        finally:
            self.running = False
