#!/bin/env python
"""
Copying Files
"""
import asyncio
import logging
import resource


class CopyFilesController:

    def __init__(
            self, list_action, copy_action, delete_action, check_dir_usage_action, limit_tasks, file_sources, limit
    ):
        self.log = logging.getLogger(self.__class__.__name__)
        self.list_files_action = list_action
        self.copy_file_action = copy_action
        self.delete_file_action = delete_action
        self.check_dir_usage_action = check_dir_usage_action
        self.limit_concurrency = limit_tasks
        self.file_sources = file_sources
        self.limit = limit

    async def __call__(self):
        self.log.debug(f"Resource usage before start: {resource.getrusage(resource.RUSAGE_SELF)}")
        tasks = [
            asyncio.create_task(self.process_source(source_name, cfg))
            for source_name, cfg in self.file_sources.items()
        ]
        await asyncio.gather(*tasks)
        self.log.debug(f"Resource usage after start: {resource.getrusage(resource.RUSAGE_SELF)}")

    async def process_source(self, source_name, cfg):
        self.log.info(f"Processing one of the sources: {source_name}")
        source_files = await self.list_files_action(cfg["incoming"], cfg.get("files_pattern", "*.*"))
        if source_files:
            self.log.info(f"Incoming File(s) Found: {len(source_files)}")
            if source_files:
                await self.process_destinations(source_files, cfg)
            if cfg.get("delete_incoming_file", True):
                tasks = [asyncio.create_task(self.delete_a_file(file)) for file in source_files]
                await asyncio.gather(*self.limit_concurrency(tasks, concurrency=self.limit))
                self.log.info(f"All Incoming Source Files Were Deleted: {len(source_files)}")
        else:
            self.log.error(f"No Source Files To Copy")
            return

    async def process_destinations(self, source_files, cfg):
        tasks = [asyncio.create_task(self.process_destination(dest, source_files)) for dest in cfg["copy_to"].values()]
        await asyncio.gather(*tasks)

    async def process_destination(self, dest_dir, source_files):
        dir_space_used = await self.check_dir_usage_action(dest_dir["dir"])
        if dir_space_used >= dest_dir["quota"]:
            self.log.warning(
                f"{dest_dir['dir']} used disk space {dir_space_used} (MB) >= "
                f"configured quota {dest_dir['quota']} (MB). NO new files in this location."
            )
            return
        tasks = [asyncio.create_task(self.process_a_file(file, dest_dir)) for file in source_files]
        await asyncio.gather(*self.limit_concurrency(tasks, concurrency=self.limit))

    async def process_a_file(self, file, dest_dir):
        await self.copy_file_action(file, dest_dir["dir"])

    async def delete_a_file(self, file):
        await self.delete_file_action(file.full)
