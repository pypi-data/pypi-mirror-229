"""
Test task for the 'high_memory' resource queue
"""
import logging
from time import sleep

from dkist_processing_core import TaskBase

logger = logging.getLogger(__name__)


class HighMemoryTask(TaskBase):
    def run(self) -> None:
        logger.info("Starting High Memory Task")
        one_gibibyte = int(9.7e9)
        use_memory = bytearray(one_gibibyte)
        logger.info(f"Using Memory {one_gibibyte = }")
        sleep(5)
        use_memory = None
        logger.info(f"Memory De-Referenced.")
