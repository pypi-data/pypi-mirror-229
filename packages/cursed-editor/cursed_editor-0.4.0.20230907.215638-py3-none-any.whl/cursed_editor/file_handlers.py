#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2023 Philip Zerull

# This file is part of "The Cursed Editor"

# "The Cursed Editor" is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

import abc
import os
import logging


logger = logging.getLogger(__name__)


class BaseFileHandler(abc.ABC):
    def read(self):
        raise NotImplementedError

    def save(self, content: str):
        raise NotImplementedError


class FileHandler(BaseFileHandler):
    def __init__(self, file_path, encoding="utf-8"):
        self._file_path = file_path
        self._encoding = encoding

    def read(self):
        if not os.path.exists(self._file_path):
            return ""
        with open(self._file_path, encoding="utf-8") as fref:
            return fref.read()

    def save(self, content: str):
        with open(self._file_path, "w", encoding="utf-8") as fref:
            fref.write(content)


class MemoryFileHandler(BaseFileHandler):
    def __init__(self, content=""):
        self._content = content

    def read(self):
        return self._content

    def save(self, content):
        self._content = content
