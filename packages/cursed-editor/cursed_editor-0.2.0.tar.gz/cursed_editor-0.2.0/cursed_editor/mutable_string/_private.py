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


class MutableString:
    def __init__(self, content):
        self._content = content

    def __repr__(self):
        return f"<MutableString content={repr(self._content)}>"

    def __str__(self):
        return self._content

    def to_string(self):
        return str(self)

    def get_character_at(self, *, index):
        return self._content[index]

    def insert_before(self, *, text, index):
        if not isinstance(text, str):
            raise TypeError("text parameter must be a str object")
        if not isinstance(index, int):
            raise TypeError("index parameter must be an int object")
        index = min(max(index, 0), len(self._content) - 1)
        before = self._content[:index]
        after = self._content[index:]
        self._content = before + text + after
        return self

    def insert_after(self, *, text, index):
        if not isinstance(text, str):
            raise TypeError("text parameter must be a str object")
        if not isinstance(index, int):
            raise TypeError("index parameter must be an int object")
        index = index + 1
        index = min(max(index, 1), len(self._content) + 1)
        before = self._content[:index]
        after = self._content[index:]
        self._content = before + text + after
        return self

    def append(self, *, text):
        if not isinstance(text, str):
            raise TypeError("text parameter must be a str object")
        self._content = self._content + text
        return self

    def prepend(self, *, text):
        if not isinstance(text, str):
            raise TypeError("text parameter must be a str object")
        self._content = text + self._content
        return self

    def delete(self, *, start=0, end=None, length=None):
        if not self._content:
            return self
        if not isinstance(start, int):
            raise TypeError("start parameter must be an int object")
        start = start % len(self._content)
        if end is not None and not isinstance(end, int):
            raise TypeError("end parameter must be an int object")
        if length is not None and not isinstance(length, int):
            raise TypeError("length parameter must be an int object")
        if length is not None and end is not None:
            raise ValueError(
                "cannot pass values for both end and length parameters"
            )
        if end is not None:
            end = end % len(self._content)
        elif length is None:
            end = len(self._content) - 1
        elif length == 0:
            return self
        elif length < 0:
            raise ValueError("length parameter must be at least zero")
        else:
            end = start + length - 1
            end = min(end, len(self._content))
        if end < start:
            raise ValueError("the end must be greater than the start")
        end = end + 1
        before = self._content[:start]
        after = self._content[end:]
        self._content = before + after
        return self

    def search(self, *, needle, case_sensitive=True):
        result = []
        if not needle:
            return result
        content = self._content
        if not case_sensitive:
            content = content.lower()
            needle = needle.lower()
        current = content.find(needle)
        while current != -1:
            result.append(current)
            current = self._content.find(needle, current + 1)
        return result
