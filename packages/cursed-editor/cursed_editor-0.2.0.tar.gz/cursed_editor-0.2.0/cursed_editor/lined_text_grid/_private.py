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

from cursed_editor import selection
from cursed_editor.coordinate import Coordinate
from cursed_editor.mutable_string import MutableString


class LinedTextGrid:
    def __init__(self, mutable_string, line_ending="\n"):
        if isinstance(mutable_string, str):
            mutable_string = MutableString(mutable_string)
        self._mutable_string = mutable_string
        self._line_ending = line_ending

    def __repr__(self):
        return f"<LinedTextGrid content={repr(str(self))}>"

    def __str__(self):
        return str(self._mutable_string)

    def to_string(self):
        return str(self)

    @property
    def line_ending(self):
        return self._line_ending

    def _get_underlying_index(self, *, coordinate=None):
        text = str(self)
        lines = text.split(self._line_ending)
        y = max(0, coordinate.y)
        if y >= len(lines):
            return len(text) - 1
        prior_lines = lines[:y]
        current_line = lines[y] + self._line_ending
        x = min(max(0, coordinate.x), len(current_line) - 1)
        current_line = current_line[:x]
        lines = prior_lines + [current_line]
        combined = self._line_ending.join(lines)
        underlying_index = len(combined)
        return underlying_index

    def coordinate_in_bounds(self, *, coordinate):
        if not self._y_coordinate_in_bounds(coordinate=coordinate):
            return False
        if coordinate.x < 0:
            return False
        text = str(self)
        lines = text.split(self._line_ending)
        line = lines[coordinate.y]
        return coordinate.x < len(line)

    def _y_coordinate_in_bounds(self, *, coordinate):
        text = str(self)
        lines = text.split(self._line_ending)
        return 0 <= coordinate.y < len(lines)

    def get_character_at(self, *, coordinate):
        index = self._get_underlying_index(coordinate=coordinate)
        return self._mutable_string.get_character_at(index=index)

    def delete(self, *, start, end):
        text = str(self)
        result = selection.except_linear(
            text=text, start=start, end=end, line_break=self.line_ending
        )
        self._mutable_string.delete()
        self.append(text=result)
        return self

    def insert_before(self, *, text, coordinate=None):
        index = self._get_underlying_index(coordinate=coordinate)
        self._mutable_string.insert_before(text=text, index=index)
        return self

    def insert_after(self, *, text, coordinate=None):
        index = self._get_underlying_index(coordinate=coordinate)
        self._mutable_string.insert_after(text=text, index=index)
        return self

    def append(self, *, text):
        self._mutable_string.append(text=text)
        return self

    def prepend(self, *, text):
        self._mutable_string.prepend(text=text)
        return self

    def lines(self, *, start=None, end=None):
        return selection.text_lines(
            text=str(self),
            line_ending=self._line_ending,
            start=start,
            end=end,
        )

    def search(self, *, needle, case_sensitive=True):
        result = []
        for index in self._mutable_string.search(
            needle=needle, case_sensitive=case_sensitive
        ):
            result.append(self._coordinate_from_index(index=index))
        return result

    def _coordinate_from_index(self, *, index):
        filtered_content = str(self)[:index]
        lines = filtered_content.split(self.line_ending)
        y = len(lines) - 1
        x = len(lines[-1])
        return Coordinate(x=x, y=y)
