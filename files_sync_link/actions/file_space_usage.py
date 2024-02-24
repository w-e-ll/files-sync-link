#!/bin/env python
"""
List files
"""
import asyncio
import logging
import os


class DirSpaceUsage:
    """ Returns used file system space in MB"""

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    async def __call__(self, directory):
        try:
            self.log.info(f"Checking {directory} usage")
            return await asyncio.to_thread(self.get_used_space, directory)
        except Exception as exc:
            self.log.error(f"Failed to Check Space Usage. EXC: {exc}")
            raise

    @staticmethod
    def get_used_space(directory):
        used_sp_bytes = os.path.getsize(directory)
        used_sp_mb = (used_sp_bytes/1024)/1024
        return int(used_sp_mb)
