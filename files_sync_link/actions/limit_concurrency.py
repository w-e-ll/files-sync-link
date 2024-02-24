#!/bin/env python
"""
Limit concurrency
"""
import asyncio


class LimitConcurrencyAction:
    """
    Decorate tasks to limit concurrency.
    Enforces a limit on the number of tasks that can run concurrently in higher
    level asyncio-compatible concurrency managers like asyncio.gather(coroutines) and
    asyncio.as_completed(coroutines).
    """
    def __call__(self, tasks, concurrency=None):
        semaphore = asyncio.Semaphore(concurrency)

        async def with_concurrency_limit(task):
            async with semaphore:
                return await task

        return [with_concurrency_limit(task) for task in tasks]
