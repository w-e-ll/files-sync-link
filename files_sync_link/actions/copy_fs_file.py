#!/bin/env python
"""
Copy file.
"""
import asyncio
import logging
import shutil


class CopyFileAction:

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    async def __call__(self, file, destination):
        try:
            self.log.info(f"Copying {file.name} to -> {destination}")
            await asyncio.to_thread(shutil.copy, file.full, destination + file.name)
        except Exception as exc:
            self.log.error(f"Failed to Copy {file.name} to {destination}. EXC: {exc}")
            raise
