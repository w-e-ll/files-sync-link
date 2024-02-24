#!/bin/env python
"""
Fetch files by SFTP
"""
import asyncio
import logging
import os
import resource


class FetchFilesController:

    def __init__(
            self, sftp_action, copy_file_action, check_disk_space_action, limit_tasks, sftp_sources, limit
    ):
        self.log = logging.getLogger(self.__class__.__name__)
        self.sftp_action = sftp_action
        self.copy_file_action = copy_file_action
        self.check_disk_space_action = check_disk_space_action
        self.sftp_sources = sftp_sources
        self.concurrency_action = limit_tasks
        self.limit = limit

    async def __call__(self):
        self.log.debug(f"Resource usage before start: {resource.getrusage(resource.RUSAGE_SELF)}")
        tasks = [
            asyncio.create_task(self.create_local_path(source["local_incoming"], source["local_archive"]))
            for sftp_key, source in self.sftp_sources.items()
        ]
        self.log.info("Creating not existing local paths for a source.")
        await asyncio.gather(*tasks)
        await self.get_sftp_files()
        self.log.debug(f"Resource usage after start: {resource.getrusage(resource.RUSAGE_SELF)}")

    async def get_sftp_files(self):
        tasks = [
            asyncio.create_task(self.get_files(sftp_key, sftp_val))
            for sftp_key, sftp_val in self.sftp_sources.items()
        ]
        await asyncio.gather(*tasks)
        self.log.info("All Tasks Completed. All Files Transferred for Every Source")

    async def get_files(self, sftp_key, sftp_source):
        self.log.info(f"Starting a Task for Source: {sftp_key}")
        if sftp_source["check_free_space"]:
            fs, free_threshold = sftp_source["check_free_space"].split(':')
            free_space = await self.check_disk_space_action(fs)
            if free_space <= int(free_threshold):
                self.log.error(f"{fs}: Free Space {free_space}(MB) <= Threshold: {free_threshold}. Flow Stopped")
                return
        else:
            self.log.error("Failed to Check Space Usage. Please Update Configuration")
            return
        if sftp_source["files"]:
            sftp_files = await self.sftp_action(self.concurrency_action, self.limit, sftp_source)
            await self.copy_to_output(sftp_files, sftp_source["local_archive"])
            self.log.info(f"Downloaded Files Copied: {len(sftp_files)} To Folder: {sftp_source['local_archive']}")
        self.log.info(f"Task is Done. Completed Sftp File Transfer for Source: : {sftp_key}")

    async def create_local_path(self, *args):
        self.log.info(f"Creating not existing local paths: {args}")
        [await asyncio.to_thread(os.makedirs, path) for path in args if not os.path.isdir(path)]

    async def copy_to_output(self, files: list, out_dir: str):
        tasks = [asyncio.create_task(self.make_copy(file, out_dir)) for file in files if os.path.isfile(file.full)]
        await asyncio.gather(*self.concurrency_action(tasks, concurrency=self.limit))

    async def make_copy(self, file: str, out_dir: str):
        await self.copy_file_action(file, out_dir)
