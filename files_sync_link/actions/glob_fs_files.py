#!/bin/env python
"""
List files.
"""
import asyncio
import logging
import os

from glob import glob

from files_sync_link.actions.describe_file import FsFile


class GlobFsFilesAction:

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    async def create_directory(self, directory):
        if not os.path.isdir(directory):
            try:
                self.log.info(f"Creating not existing local directory: {directory}")
                await asyncio.to_thread(os.makedirs, directory)
            except Exception as exc:
                self.log.error(f"Failed to Create Directory. EXC: {exc}")
                raise

    async def listing_files(self, directory):
        try:
            self.log.info(f"Listing files in the directory: {directory}")
            return await asyncio.to_thread(glob, directory)
        except Exception as exc:
            self.log.error(f"Failed to List Files. EXC: {exc}")
            raise

    async def __call__(self, directory, pattern):
        result = []
        await self.create_directory(directory)
        directory = os.path.join(directory, pattern)
        files = await self.listing_files(directory)
        [result.append(FsFile(file)) for file in files]
        return result
