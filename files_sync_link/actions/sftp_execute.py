#!/bin/env python
"""
SFTP utility
"""
import asyncio
import asyncssh
import logging

from files_sync_link.actions.describe_file import FsFile


class SFTPClient:
    """SFTP Client Connects to a Server and Works With Files"""
    def __init__(self, limit_concurrency, limit, config: dict = None):
        self.host = config['host']
        self.port = int(config['port']) if 'port' in config else 22
        self.username = config['username']
        self.password = config['password'] if 'password' in config else None
        self.source = config['source']
        self.files = config['files']
        self.local_incoming = config['local_incoming']
        self.passphrase = config['passphrase'] if 'passphrase' in config else None
        self.ssh_key = config['ssh_key'] if 'ssh_key' in config and isinstance(config['ssh_key'], list) else []
        self.limit_concurrency = limit_concurrency
        self.limit = limit

    async def run_client(self, log):
        async with asyncssh.connect(
                host=self.host, username=self.username, port=self.port,
                password=self.password, client_keys=[self.ssh_key[0]]) as conn:
            async with conn.start_sftp_client() as sftp:
                log.info(f"Connected to Remote Server: {self.host}")
                files = await self.list_files(log, sftp)
                if files:
                    log.info(f"Listed Files to Download: {len(files)}")
                    tasks = [
                        asyncio.create_task(self.download_file(log, sftp, file))
                        for file in files
                    ]
                    await asyncio.gather(*self.limit_concurrency(tasks, concurrency=self.limit))
                    files = [FsFile(file) for file in files]
                    log.info(f"Downloaded Files: {len(files)} are in Folder: {self.local_incoming}")
                    return files
                log.info(f"No Files Were Downloaded")
                return

    async def list_files(self, log, sftp):
        try:
            return await sftp.glob(self.source + self.files)
        except asyncssh.SFTPError as exc:
            log.info(f"Unable to List Files: {exc}")
            raise

    async def download_file(self, log, sftp, file):
        try:
            await sftp.get(file, localpath=self.local_incoming)
        except asyncssh.SFTPError as exc:
            log.info(f"Unable to Get Files: {exc}")
            raise


class ExecuteSFTPAction:
    """Executes SFTPClient class and handles Exceptions"""
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    async def __call__(self, limit_concurrency, limit, config):
        driver = SFTPClient(limit_concurrency, limit, config)
        try:
            return await driver.run_client(self.log)
        except (OSError, asyncssh.Error) as exc:
            self.log.error(f"SSH connection failed. EXC: {exc}")
            raise
