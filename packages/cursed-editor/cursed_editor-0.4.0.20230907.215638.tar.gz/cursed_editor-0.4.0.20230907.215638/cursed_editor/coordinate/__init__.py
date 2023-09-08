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

from . import _private


class Coordinate(_private.Coordinate):
    """A Coordinate object is used to represent the x and y coordinates of
    a two dimantional integer based grid.
    """

    def __init__(self, *, x: int, y: int):
        """Create a new Coordinate using integer values for x and y

        >>> Coordinate(x=1, y=2)
        <Coordinate x=1, y=2>
        """
        super().__init__(x=x, y=y)

    def __add__(self, other):
        """Adds two Coordinate objects together to produce a new one.
        >>> Coordinate(x=1, y=2) + Coordinate(x=4, y=8)
        <Coordinate x=5, y=10>

        This will raise a type error if attempting to add something
        other than a coordinate.

        >>> Coordinate(x=1, y=2) + 5
        Traceback (most recent call last):
        TypeError: Can only add Coordinates to Coordinates
        """
        return super().__add__(other)

    def __sub__(self, other):
        """Subtracts two Coordinate objects together to produce a new one.
        >>> Coordinate(x=100, y=200) - Coordinate(x=4, y=8)
        <Coordinate x=96, y=192>

        This will raise a type error if attempting to add something
        other than a Coordinate.

        >>> Coordinate(x=1, y=2) - 5
        Traceback (most recent call last):
        TypeError: Can only subtract Coordinates from Coordinates
        """
        return super().__sub__(other)

    def __eq__(self, other):
        """Compares two Coordinate objects for equality.  Coordinates are
        equal if both the x and y components are the same
        >>> Coordinate(x=1, y=2) == Coordinate(x=1, y=2)
        True

        >>> Coordinate(x=1, y=2) == Coordinate(x=0, y=2)
        False

        >>> Coordinate(x=1, y=2) == Coordinate(x=1, y=0)
        False

        >>> Coordinate(x=1, y=2) == Coordinate(x=-1, y=-2)
        False

        This will raise a type error if attempting to compare a Coordinate
        to something other than a Coordinate.

        >>> Coordinate(x=1, y=2) == 5
        Traceback (most recent call last):
        TypeError: can only compare Coordinates to other Coordinates
        """
        return super().__eq__(other)

    def __gt__(self, other):
        """Checks if this Coordinate is greater than the other Coordiante.

        >>> Coordinate(x=5, y=5) > Coordinate(x=2, y=2)
        True

        >>> Coordinate(x=5, y=5) > Coordinate(x=2, y=5)
        True

        >>> Coordinate(x=50, y=5) > Coordinate(x=2, y=5)
        True

        >>> Coordinate(x=0, y=50) > Coordinate(x=2, y=5)
        True

        This will raise a type error if attempting to compare a Coordinate
        to something other than a Coordinate.

        >>> Coordinate(x=1, y=2) > 5
        Traceback (most recent call last):
        TypeError: can only compare Coordinates to other Coordinates
        """
        return super().__gt__(other)

    def __ge__(self, other):
        return (self == other) or (self > other)
