#!/bin/env python
"""
Delete a file.
"""
import asyncio
import logging
import os


class DeleteFileAction:

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    async def __call__(self, file):
        try:
            self.log.info(f"Removing {file}")
            await asyncio.to_thread(os.remove, file)
        except Exception as exc:
            self.log.error(f"Failed to Remove {file}. EXC: {exc}")
            raise
