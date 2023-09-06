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


class Coordinate:
    def __init__(self, *, x: int, y: int):
        self._x = x
        self._y = y

    def __repr__(self):
        return f"<Coordinate x={self.x}, y={self.y}>"

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __add__(self, other):
        if not isinstance(other, Coordinate):
            raise TypeError("Can only add Coordinates to Coordinates")
        return Coordinate(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Coordinate):
            raise TypeError("Can only subtract Coordinates from Coordinates")
        return Coordinate(x=self.x - other.x, y=self.y - other.y)

    def __eq__(self, other):
        if not isinstance(other, Coordinate):
            raise TypeError("can only compare Coordinates to other Coordinates")
        return self.x == other.x and self.y == other.y

    def __gt__(self, other):
        if not isinstance(other, Coordinate):
            raise TypeError("can only compare Coordinates to other Coordinates")
        return (self.y > other.y) or (self.y == other.y and self.x > other.x)
