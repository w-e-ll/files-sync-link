#!/bin/env python
"""
File Object
"""
import os


class FsFile:

    def __init__(self, file):
        self.full = file
        self.path = os.path.split(file)[0]
        self.size = os.stat(file).st_size
        self.name = os.path.basename(file)
