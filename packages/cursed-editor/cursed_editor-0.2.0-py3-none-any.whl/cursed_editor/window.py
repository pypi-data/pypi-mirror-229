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


class Window:
    def __init__(self, *, width=50, height=50, top=0, left=0):
        self.width = width
        self.height = height
        self.top = top
        self.left = left

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, new_width):
        self._width = max(new_width, 0)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, new_height):
        self._height = max(new_height, 0)

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, new_top):
        self._top = max(new_top, 0)

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, new_left):
        self._left = max(new_left, 0)

    @property
    def right(self):
        return self.left + self.width

    @right.setter
    def right(self, new_right):
        self.left = new_right - self.width

    @property
    def bottom(self):
        return self.top + self.height - 1

    @bottom.setter
    def bottom(self, new_bottom):
        self.top = new_bottom - self.height

    def move_to_contain_coordinate(self, coordinate):
        coordinate_left_of_window = coordinate.x < self.left
        coordinate_right_of_window = coordinate.x >= self.right
        coordinate_above_window = coordinate.y < self.top
        coordinate_below_window = coordinate.y >= self.bottom
        if coordinate_left_of_window:
            self.left = coordinate.x
        if coordinate_right_of_window:
            self.right = coordinate.x + 1
        if coordinate_above_window:
            self.top = coordinate.y
        if coordinate_below_window:
            self.bottom = coordinate.y + 1
