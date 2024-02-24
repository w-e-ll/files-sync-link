#!/bin/env python
"""
Application.
"""
import asyncio
import argparse
import logging
import os
import signal
import yaml

from files_sync_link import init_logging
from files_sync_link.controllers.fetch_files import FetchFilesController
from files_sync_link.actions.copy_fs_file import CopyFileAction
from files_sync_link.actions.sftp_execute import ExecuteSFTPAction
from files_sync_link.actions.disk_free_space import DiskFreeSpace
from files_sync_link.actions.limit_concurrency import LimitConcurrencyAction


class DistributeFilesApp:

    def __init__(self, cfg, stop_on_loop):
        self.log = logging.getLogger(self.__class__.__name__)
        self.cfg = cfg
        self.loops = 0
        self.stop_on_loop = stop_on_loop
        self.sftp_sources = cfg["sftp_sources"]
        self.controller = None
        self.sftp_jobs = cfg["scheduler"]["sftp_jobs"]
        self.check_timeout = cfg["scheduler"]["sftp_check_timeout"]
        self.sftp_batch_size = cfg["sftp_batch_size"]
        self.sftp_timeout = cfg["sftp_timeout"]
        self.tasks_limit = cfg["concurrency_limit"]["limit"]

    async def run_one_loop(self):
        self.loops += 1
        self.log.info(f"Running Loop #{self.loops}...")
        try:
            await self.controller()
            self.log.info(f"Run #{self.loops} is Completed.")
        except Exception as exc:
            self.log.error(f"Run #{self.loops} is Completed with Error. EXC: {exc}")
            raise

    async def run_loops(self):
        while True:
            await self.run_one_loop()
            if self.stop_on_loop and self.stop_on_loop == self.loops:
                self.log.info(f"Stopping After Loop {self.loops} == {self.stop_on_loop}")
                break
            await asyncio.sleep(self.check_timeout)

    async def run(self):
        self.log.info("Alive")
        self.controller = FetchFilesController(
            ExecuteSFTPAction(), CopyFileAction(), DiskFreeSpace(),
            LimitConcurrencyAction(), self.sftp_sources, self.tasks_limit
        )
        await self.run_loops()


async def main(arguments):
    """Entry Point"""
    try:
        init_logging(arguments)
        config = yaml.safe_load(arguments.config)
        app = DistributeFilesApp(config, arguments.stop_on_loop)
    except Exception as exc:
        logging.error(f"Failed to Initialize. EXC: {exc}")
        raise

    await app.run()
    logging.info("Main Finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="append_const", const=1)
    parser.add_argument("--config", nargs="?", type=argparse.FileType("r"), default="etc/config.yml")
    parser.add_argument("--stop-on-loop", default=None, type=int, required=False)
    args = parser.parse_args()
    try:
        asyncio.run(main(args))
    finally:
        logging.info(f"main finished on loop {args.stop_on_loop}")
        if not args.stop_on_loop:
            os.killpg(0, signal.SIGKILL)
