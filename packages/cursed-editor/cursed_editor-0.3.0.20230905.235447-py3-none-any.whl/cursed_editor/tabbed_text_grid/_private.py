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

import logging

from cursed_editor import selection
from cursed_editor.coordinate import Coordinate

logger = logging.getLogger(__name__)


class TabExpandingTextGrid:
    def __init__(self, lined_text_grid, tab_size=4):
        self._lined_text_grid = lined_text_grid
        self._tab_size = tab_size

    def __repr__(self):
        return f"<TabExpandingTextGrid content={repr(str(self))}>"

    def __str__(self):
        return self.get_expanded_text()

    def get_expanded_text(self):
        text = self.get_unexpanded_text()
        return text.replace("\t", "\t" * self._tab_size)

    def get_unexpanded_text(self):
        return str(self._lined_text_grid)

    def _get_underlying_coordinate(self, *, coordinate=None):
        if coordinate is None:
            coordinate = Coordinate(x=0, y=0)
        y = coordinate.y
        line = self._lined_text_grid.lines(start=y, end=y)[0]
        ending = self._lined_text_grid.line_ending
        line = line.replace("\t", "\t" * self._tab_size) + ending
        x = min(max(0, coordinate.x), len(line) - 1)
        line = line[:x]
        splitup = line.split("\t" * self._tab_size)
        last = splitup.pop().rstrip("\t")
        splitup.append(last)
        line = "\t".join(splitup)
        return Coordinate(y=y, x=len(line))

    def _get_coordinate_from_underlying(self, *, underlying):
        y = underlying.y
        line = self._lined_text_grid.lines(start=y, end=y)[0]
        line = line[: underlying.x]
        line = line.replace("\t", "\t" * self._tab_size)
        x = len(line)
        return Coordinate(x=x, y=y)

    def get_tab_aligned_coordinate(self, *, coordinate):
        underlying = self._get_underlying_coordinate(coordinate=coordinate)
        return self._get_coordinate_from_underlying(underlying=underlying)

    def get_character_at(self, *, coordinate):
        underlying = self._get_underlying_coordinate(coordinate=coordinate)
        return self._lined_text_grid.get_character_at(coordinate=underlying)

    def insert_before(self, *, text, coordinate=None):
        underlying = self._get_underlying_coordinate(coordinate=coordinate)
        self._lined_text_grid.insert_before(text=text, coordinate=underlying)
        return self

    def insert_after(self, *, text, coordinate=None):
        underlying = self._get_underlying_coordinate(coordinate=coordinate)
        self._lined_text_grid.insert_after(text=text, coordinate=underlying)
        return self

    def smart_insert(self, *, text, coordinate=None):
        if self.coordinate_is_after_content(coordinate=coordinate):
            logger.info("inserting after")
            self.insert_after(text=text, coordinate=coordinate)
        else:
            logger.info("inserting before")
            self.insert_before(text=text, coordinate=coordinate)

    def coordinate_is_after_content(self, *, coordinate):
        result = False
        lines = self.lines()
        max_y = len(lines) - 1
        max_x = len(lines[-1]) - 1
        if coordinate.y > max_y:
            result = True
        elif coordinate.y == max_y:
            result = coordinate.x >= max_x
        return result

    def append(self, *, text):
        self._lined_text_grid.append(text=text)
        return self

    def delete(self, *, start, end):
        start_index = self._get_underlying_coordinate(coordinate=start)
        end_index = self._get_underlying_coordinate(coordinate=end)
        self._lined_text_grid.delete(start=start_index, end=end_index)
        return self

    def lines(self, *, start=None, end=None):
        return selection.text_lines(
            text=str(self),
            line_ending=self._lined_text_grid.line_ending,
            start=start,
            end=end,
        )

    def get_moved_coordinate(
        self,
        *,
        coordinate,
        new_x=None,
        new_y=None,
        up=0,
        down=0,
        left=0,
        right=0,
    ):
        underlying = self._get_underlying_coordinate(coordinate=coordinate)
        if new_y is None:
            new_y = underlying.y
        new_y = new_y + down - up
        new_y = min(max(0, new_y), len(self._lined_text_grid.lines()) - 1)
        current_line = self._lined_text_grid.lines(start=new_y, end=new_y)[0]
        if new_x is None:
            new_x = underlying.x
        elif new_x == -1:
            new_x = len(current_line)
        new_x = new_x + right - left
        new_x = min(max(0, new_x), len(current_line))
        new_underlying = Coordinate(x=new_x, y=new_y)
        return self._get_coordinate_from_underlying(underlying=new_underlying)

    def search(self, *, needle, case_sensitive=True):
        result = []
        for underlying in self._lined_text_grid.search(
            needle=needle, case_sensitive=case_sensitive
        ):
            coord = self._get_coordinate_from_underlying(underlying=underlying)
            result.append(coord)
        return result
