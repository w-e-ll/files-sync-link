#!/bin/env python
"""
List files.
"""
import asyncio
import logging
import os


class DiskFreeSpace:
    """ Returns free file system space in MB"""

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    async def __call__(self, file_system):
        try:
            self.log.info(f"Checking {file_system} free space")
            return await asyncio.to_thread(self.get_free_space, file_system)
        except Exception as exc:
            self.log.error(f"Failed to Check Free Space. EXC: {exc}")
            raise

    @staticmethod
    def get_free_space(fs):
        st = os.statvfs(fs)
        free = st.f_bavail * st.f_frsize
        return int((free/1024)/1024)
