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

from cursed_editor.coordinate import Coordinate
from cursed_editor.mutable_string import MutableString

from . import _private


class LinedTextGrid(_private.LinedTextGrid):
    def __init__(self, mutable_string, line_ending="\n"):
        """Create a new LinedTextGrid by either providing a str or MutableString.
        >>> LinedTextGrid("hello")
        <LinedTextGrid content='hello'>

        >>> LinedTextGrid(MutableString("hello"))
        <LinedTextGrid content='hello'>
        """
        super().__init__(mutable_string, line_ending="\n")

    def __str__(self):
        """Returns the contents of the LinedTextGrid as a str
        >>> str(LinedTextGrid("a b c d e f g"))
        'a b c d e f g'
        """
        return super().__str__()

    def to_string(self):
        """Equivalent to str(self).  Helpful for method chaining.
        >>> LinedTextGrid("a b c d e f g").to_string()
        'a b c d e f g'
        """
        return super().to_string()

    def coordinate_in_bounds(self, *, coordinate):
        r"""Checks to see if the coordinate is in the bounds of the string.

        >>> grid = LinedTextGrid("first\nsecond\nthird")
        >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=1, y=1))
        True
        >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=-1, y=1))
        False
        >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=5, y=1))
        True
        >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=6, y=1))
        False
        >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=7000, y=1))
        False
        >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=3, y=-1))
        False
        >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=3, y=10))
        False
        """
        return super().coordinate_in_bounds(coordinate=coordinate)

    def delete(self, *, start, end):
        r"""Deletes text between the given coordinates (inclusive).

        >>> grid = LinedTextGrid("first\nsecond\nthird")
        >>> grid.delete(start=Coordinate(x=0, y=1), end=Coordinate(x=0, y=2))
        <LinedTextGrid content='first\nhird'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
        >>> grid.delete(start=Coordinate(x=0, y=3), end=Coordinate(x=100, y=3))
        <LinedTextGrid content='first\nsecond\nthird\nfifth\n'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
        >>> grid.delete(start=Coordinate(x=-8, y=3), end=Coordinate(x=100, y=3))
        <LinedTextGrid content='first\nsecond\nthird\nfifth\n'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
        >>> grid.delete(start=Coordinate(x=99, y=2), end=Coordinate(x=99, y=3))
        <LinedTextGrid content='first\nsecond\nthird\nfifth\n'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
        >>> grid.delete(start=Coordinate(x=-100, y=3), end=Coordinate(x=2, y=3))
        <LinedTextGrid content='first\nsecond\nthird\nrth\nfifth\n'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
        >>> grid.delete(start=Coordinate(x=0, y=2), end=Coordinate(x=100, y=100))
        <LinedTextGrid content='first\nsecond\n'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
        >>> grid.delete(start=Coordinate(x=8, y=-1), end=Coordinate(x=5, y=2))
        <LinedTextGrid content='fourth\nfifth\n'>

        """
        return super().delete(start=start, end=end)

    def get_character_at(self, *, coordinate):
        """Returns the character at the given coordinate.

        >>> grid = LinedTextGrid("a b c d e f g")
        >>> grid.get_character_at(coordinate=Coordinate(x=6, y=0))
        'd'
        """
        return super().get_character_at(coordinate=coordinate)

    @property
    def line_ending(self):
        r"""Returns the LinedTextGrid's line ending sequence.

        >>> LinedTextGrid("first\nsecond\nthird\n").line_ending
        '\n'
        """
        return super().line_ending

    def insert_before(self, *, text, coordinate=None):
        r"""Inserts text before the given coordinate.

        The text argument must be a str.
        The index argument must be an int.

        The provided coordinate will be automatically bounded so that
        the y coordinate is between 0 and the number of lines minus one,
        and the x coordinate is between 0 and the length of line y minus one.

        As a result, this method cannot be used to append text to the end of
        the string.  To do that, call either the append or insert_after methods.

        Since we treat the line_ending character as the last character on
        each line, this can be used to append text "to the end" of a line.
        However to insert a new line between lines using this method, you
        need to insert a string which ends with the line_ending character
        sequence at the coordinate prior to the beginning of the line which,
        after inserting the new text, will follow the newly inserted text.

        This method returns a reference to self to support method chaining.

        Examples:

        >>> grid = LinedTextGrid("first\nsecond\nthird\n")
        >>> grid.insert_before(text="half\n", coordinate=Coordinate(y=1,x=0))
        <LinedTextGrid content='first\nhalf\nsecond\nthird\n'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\n")
        >>> grid.insert_before(text="half\n", coordinate=Coordinate(y=0,x=-1))
        <LinedTextGrid content='half\nfirst\nsecond\nthird\n'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\n")
        >>> grid.insert_before(text="half\n", coordinate=Coordinate(y=-1,x=0))
        <LinedTextGrid content='half\nfirst\nsecond\nthird\n'>

        >>> grid2 = LinedTextGrid("first\nsecond\nthird\n")
        >>> grid2.insert_before(text="half\n", coordinate=Coordinate(y=10,x=0))
        <LinedTextGrid content='first\nsecond\nthirdhalf\n\n'>

        >>> grid2 = LinedTextGrid("")
        >>> grid2.insert_before(text="half\n", coordinate=Coordinate(y=10,x=0))
        <LinedTextGrid content='half\n'>

        >>> grid2 = LinedTextGrid("first\nsecond\nthird\n")
        >>> grid2.insert_before(text="half\n", coordinate=Coordinate(y=0,x=10))
        <LinedTextGrid content='firsthalf\n\nsecond\nthird\n'>
        """
        return super().insert_before(text=text, coordinate=coordinate)

    def insert_after(self, *, text, coordinate=None):
        r"""Inserts text after the given coordinate.

        The text argument must be a str.
        The index argument must be an int.

        The provided coordinate will be automatically bounded so that
        the y coordinate is between 0 and the number of lines minus one,
        and the x coordinate is between 0 and the length of line y minus one.

        As a result, this method cannot be used to prepend text to the beginning
        of the string.  To do that, call either the prepend or insert_before
        methods.

        Since we treat the line_ending character as the last character on
        each line, this can be used to append text to the beginning of a line.
        However to insert a new line between lines using this method, you
        would need to insert a string which ends with the line_ending character
        sequence to the coordinate which is the end of the line which, after
        inserting, will become the line prior to the newly inserted text.

        This method returns a reference to self to support method chaining.

        Examples:

        >>> grid = LinedTextGrid("first\nsecond\nthird\n")
        >>> grid.insert_after(text="half\n", coordinate=Coordinate(y=1,x=6))
        <LinedTextGrid content='first\nsecond\nhalf\nthird\n'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\n")
        >>> grid.insert_after(text="ifth\nf", coordinate=Coordinate(y=0,x=-1))
        <LinedTextGrid content='fifth\nfirst\nsecond\nthird\n'>

        >>> grid = LinedTextGrid("first\nsecond\nthird\n")
        >>> grid.insert_after(text="ifth\nf", coordinate=Coordinate(y=0,x=-1))
        <LinedTextGrid content='fifth\nfirst\nsecond\nthird\n'>

        >>> grid2 = LinedTextGrid("first\nsecond\nlast\n")
        >>> grid2.insert_after(text="new end", coordinate=Coordinate(y=10,x=1))
        <LinedTextGrid content='first\nsecond\nlast\nnew end'>

        >>> grid2 = LinedTextGrid("")
        >>> grid2.insert_after(text="half\n", coordinate=Coordinate(y=10,x=0))
        <LinedTextGrid content='half\n'>

        >>> grid2 = LinedTextGrid("first\nsecond\nthird\n")
        >>> grid2.insert_after(text="half\n", coordinate=Coordinate(y=0,x=10))
        <LinedTextGrid content='first\nhalf\nsecond\nthird\n'>
        """
        return super().insert_after(text=text, coordinate=coordinate)

    def append(self, *, text):
        r"""Appends the given text to the underlying value.
        Return a reference to self to support method chaining.

        >>> LinedTextGrid("I eat\n").append(text="red meat")
        <LinedTextGrid content='I eat\nred meat'>

        This will raise a ValueError if the text is not a string

        >>> LinedTextGrid("I eat\n").append(text=8)
        Traceback (most recent call last):
        TypeError: text parameter must be a str object
        """
        return super().append(text=text)

    def prepend(self, *, text):
        r"""Prepends the given text to the underlying value.
        Return a reference to self to support method chaining.

        >>> LinedTextGrid("red meat\n").prepend(text="I eat ")
        <LinedTextGrid content='I eat red meat\n'>

        This will raise a ValueError if the text is not a string

        >>> LinedTextGrid("I eat\n").prepend(text=8)
        Traceback (most recent call last):
        TypeError: text parameter must be a str object
        """
        return super().prepend(text=text)

    def lines(self, *, start=None, end=None):
        r"""Returns a list of strings containing the text of lines between
        start and end (inclusive).

        >>> grid = LinedTextGrid("zero\none\ntwo\nthree\nfour\nfive\nsix")
        >>> grid.lines(start=2, end=4)
        ['two', 'three', 'four']

        >>> grid.lines(start=5, end=5)
        ['five']

        If end is not provided, then this will return all lines starting
        at start and proceeding to the end of the string

        >>> grid.lines(start=3)
        ['three', 'four', 'five', 'six']

        Similarly, if start is not provided, then this will return all
        lines from the beginning of the string through end.

        >>> grid.lines(end=3)
        ['zero', 'one', 'two', 'three']

        If both start and end are ommitted, then all lines are returned.

        >>> grid.lines()
        ['zero', 'one', 'two', 'three', 'four', 'five', 'six']

        Naturally, start and end, must be ints

        >>> grid.lines(start="moose")
        Traceback (most recent call last):
        TypeError: start parameter must be either None or an int

        >>> grid.lines(end="moose")
        Traceback (most recent call last):
        TypeError: end parameter must be either None or an int

        The start and end parameters are automatically capped to be at
        least zero and at most the number of lines minus one.

        >>> grid.lines(start=-1)
        ['zero', 'one', 'two', 'three', 'four', 'five', 'six']

        >>> grid.lines(start=7)
        ['six']

        And end must be greater than or equal to start and less than
        the number of lines in the string.

        >>> grid.lines(start=4, end=3)
        Traceback (most recent call last):
        ValueError: end must be greater than start

        >>> grid.lines(start=4, end=7)
        ['four', 'five', 'six']
        """
        return super().lines(start=start, end=end)

    def search(self, *, needle, case_sensitive=True):
        r"""Search the text for the string contained in the needle parameter.

        Returns a list containing the the Coordiante of the starting positions
        where the string is found.

        >>> haystack = "the rain\nin west\tspain\nmainly\ndrains in the plain."
        >>> grid = LinedTextGrid(haystack)

        >>> grid.search(needle="goober")
        []

        >>> result = grid.search(needle="ain")
        >>> for item in result:
        ...    print(item)
        <Coordinate x=5, y=0>
        <Coordinate x=10, y=1>
        <Coordinate x=1, y=2>
        <Coordinate x=2, y=3>
        <Coordinate x=16, y=3>

        """
        return super().search(needle=needle, case_sensitive=case_sensitive)
