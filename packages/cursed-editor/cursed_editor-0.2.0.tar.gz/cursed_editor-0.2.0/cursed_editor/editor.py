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

from .window import Window
from .coordinate import Coordinate
from .mutable_string import MutableString
from .lined_text_grid import LinedTextGrid
from .tabbed_text_grid import TabExpandingTextGrid


logger = logging.getLogger(__name__)


class Editor:
    def __init__(self, file_handler, line_ending="\n", tab_size=4):
        self.line_ending = line_ending
        self._tab_size = tab_size
        self._file_handler = file_handler
        self._mutable_string = MutableString(file_handler.read())
        self._text_grid = LinedTextGrid(self._mutable_string)
        self._tab_text_grid = TabExpandingTextGrid(self._text_grid)
        self.cursor = Coordinate(x=0, y=0)
        self.window = Window(width=50, height=50)

    def handle_delete(self):
        self._tab_text_grid.delete(start=self.cursor, end=self.cursor)

    def handle_backspace(self):
        if self.cursor.x == 0:
            self._handle_backspace_on_first_column()
        else:
            self._handle_backspace_on_nonfirst_column()

    def _handle_backspace_on_first_column(self):
        if self.cursor.y > 0:
            self.move_cursor(up=1, x=-1)
            self.handle_delete()

    def _handle_backspace_on_nonfirst_column(self):
        self.move_cursor(left=1)
        self.handle_delete()

    def handle_enter(self):
        self._tab_text_grid.smart_insert(text="\n", coordinate=self.cursor)
        self.move_cursor(down=1, x=0)

    def insert_before(self, character_to_add):
        self._tab_text_grid.smart_insert(
            text=character_to_add, coordinate=self.cursor
        )
        self.move_cursor(right=1)

    def move_cursor(self, *, x=None, y=None, up=0, down=0, left=0, right=0):
        logger.info(f"moving: {x=} {y=} {up=} {down=} {left=} {right=}")
        new_coordinate = self._tab_text_grid.get_moved_coordinate(
            coordinate=self.cursor,
            new_x=x,
            new_y=y,
            up=up,
            down=down,
            left=left,
            right=right,
        )
        logger.info(f"moving from {self.cursor} to {new_coordinate}")
        self.cursor = new_coordinate
        self.window.move_to_contain_coordinate(self.cursor)

    def cell_under_cursor(self):
        return self._tab_text_grid.get_character_at(coordinate=self.cursor)

    @property
    def window_cursor_x(self):
        self.window.move_to_contain_coordinate(self.cursor)
        return self.cursor.x - self.window.left

    @property
    def window_cursor_y(self):
        self.window.move_to_contain_coordinate(self.cursor)
        return self.cursor.y - self.window.top

    def get_text_for_window(self):
        top = self.window.top
        bottom = self.window.bottom
        lines = self._tab_text_grid.lines(start=top, end=bottom)
        final_lines = []
        for line in lines:
            line_segment = line[self.window.left : self.window.right]
            final_lines.append("".join(cell for cell in line_segment))
        return self.line_ending.join(final_lines)

    def incremental_search(
        self, search_string, mode="normal", case_sensitive=True
    ):
        positions = self._tab_text_grid.search(
            needle=search_string, case_sensitive=case_sensitive
        )
        if mode == "reverse":
            positions.reverse()
        move_to = None
        for position in positions:
            if mode == "reverse" and position < self.cursor:
                move_to = position
                break
            if mode == "normal" and position > self.cursor:
                move_to = position
                break
            if mode == "same" and position >= self.cursor:
                move_to = position
                break
        if move_to is None and positions:
            move_to = positions[0]
        if move_to is not None:
            self.move_cursor(x=move_to.x, y=move_to.y)

    def get_full_text(self):
        return self._tab_text_grid.get_unexpanded_text()

    def save(self):
        self._file_handler.save(self.get_full_text())
