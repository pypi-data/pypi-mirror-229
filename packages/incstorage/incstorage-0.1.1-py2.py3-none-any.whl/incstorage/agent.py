import asyncio
import sys
import traceback

from typing import List


# ----------------------------------------------------------
# loggers
# ----------------------------------------------------------
from pycelium.tools.logs import logger

log = logger(__name__)

# ----------------------------------------------------------
# Engine
# ----------------------------------------------------------


class Agent:
    """TBD"""

    def __init__(self):
        self.running = False

    async def main(self, max_run=sys.float_info.max):
        log.debug(f"starting agent: {self}")
        self.running = True
