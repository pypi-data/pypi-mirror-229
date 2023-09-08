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
from cursed_editor.lined_text_grid import LinedTextGrid

from . import _private


class TabExpandingTextGrid(_private.TabExpandingTextGrid):
    def __init__(self, lined_text_grid, tab_size=4):
        r"""Create a new TabExpandingTextGrid by providing a LinedTextGrid
        and the tab_size (which defaults to four).

        >>> TabExpandingTextGrid(LinedTextGrid("\thello"))
        <TabExpandingTextGrid content='\t\t\t\thello'>

        >>> TabExpandingTextGrid(LinedTextGrid("\thello"), tab_size=2)
        <TabExpandingTextGrid content='\t\thello'>
        """
        super().__init__(lined_text_grid=lined_text_grid, tab_size=tab_size)

    def insert_before(self, *, text, coordinate=None):
        r"""Inserts text before the given coordinate.

        The text argument must be a str.
        the coordinate argument must be a Coordinate.

        The provided coordinate will be automatically bounded so that
        the y coordinate is between 0 and the number of lines minus one,
        and the x coordinate is betwen 0 and the length of the line y minus one.

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


        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_before(text="people", coordinate=Coordinate(x=7, y=0))
        <TabExpandingTextGrid content='hellopeople\t\t\t\t\t\t\t\tperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_before(text="howdy, ")
        <TabExpandingTextGrid content='howdy, hello\t\t\t\t\t\t\t\tperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_before(text="Hi ", coordinate=Coordinate(x=-10, y=0))
        <TabExpandingTextGrid content='Hi hello\t\t\t\t\t\t\t\tperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_before(text="people", coordinate=Coordinate(x=9, y=0))
        <TabExpandingTextGrid content='hello\t\t\t\tpeople\t\t\t\tperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_before(text="people", coordinate=Coordinate(x=11, y=0))
        <TabExpandingTextGrid content='hello\t\t\t\tpeople\t\t\t\tperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_before(text="people", coordinate=Coordinate(x=13, y=0))
        <TabExpandingTextGrid content='hello\t\t\t\t\t\t\t\tpeopleperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\n\tperson"))
        >>> grid.insert_before(text="Hi", coordinate=Coordinate(x=100, y=0))
        <TabExpandingTextGrid content='hello\t\t\t\tHi\n\t\t\t\tperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\n\tperson"))
        >>> grid.insert_before(text="!!!", coordinate=Coordinate(x=100, y=100))
        <TabExpandingTextGrid content='hello\t\t\t\t\n\t\t\t\tperso!!!n'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("1"))
        >>> grid.insert_before(text="people", coordinate=Coordinate(x=0, y=0))
        <TabExpandingTextGrid content='people1'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("1"))
        >>> grid.insert_before(text="people", coordinate=Coordinate(x=0, y=-10))
        <TabExpandingTextGrid content='people1'>
        """
        return super().insert_before(text=text, coordinate=coordinate)

    def insert_after(self, *, text, coordinate=None):
        r"""Inserts text at the given coordinate. Returns self to support
        method chaining.

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_after(text="people", coordinate=Coordinate(x=7, y=0))
        <TabExpandingTextGrid content='hello\t\t\t\tpeople\t\t\t\tperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_after(text="people\n", coordinate=Coordinate(x=9, y=0))
        <TabExpandingTextGrid content='hello\t\t\t\t\t\t\t\tpeople\nperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_after(text="people", coordinate=Coordinate(x=11, y=0))
        <TabExpandingTextGrid content='hello\t\t\t\t\t\t\t\tpeopleperson'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("hello\t\tperson"))
        >>> grid.insert_after(text="eople P", coordinate=Coordinate(x=13, y=0))
        <TabExpandingTextGrid content='hello\t\t\t\t\t\t\t\tpeople Person'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("1"))
        >>> grid.insert_after(text="people", coordinate=Coordinate(x=0, y=0))
        <TabExpandingTextGrid content='1people'>
        """
        return super().insert_after(text=text, coordinate=coordinate)

    def append(self, *, text):
        r"""Appends the given text to the underlying value.
        Return a reference to self to support method chaining.

        >>> grid = TabExpandingTextGrid(LinedTextGrid("I eat\n"))
        >>> grid.append(text="red meat")
        <TabExpandingTextGrid content='I eat\nred meat'>

        This will raise a ValueError if the text is not a string

        >>> grid.append(text=8)
        Traceback (most recent call last):
        TypeError: text parameter must be a str object
        """
        return super().append(text=text)

    def delete(self, *, start, end):
        r"""Deletes text between the given coordinates (inclusive).

        >>> grid = TabExpandingTextGrid(LinedTextGrid("first\n\tsecond\n\tthird"))
        >>> grid.delete(start=Coordinate(x=2, y=1), end=Coordinate(x=1, y=2))
        <TabExpandingTextGrid content='first\nthird'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("first\n\tsecond\n\tthird"))
        >>> grid
        <TabExpandingTextGrid content='first\n\t\t\t\tsecond\n\t\t\t\tthird'>

        >>> grid.delete(start=Coordinate(x=2, y=1), end=Coordinate(x=2, y=1))
        <TabExpandingTextGrid content='first\nsecond\n\t\t\t\tthird'>

        >>> grid = TabExpandingTextGrid(LinedTextGrid("\tthis\thas\tlots"))
        >>> grid.delete(start=Coordinate(x=9, y=0), end=Coordinate(x=9, y=0))
        <TabExpandingTextGrid content='\t\t\t\tthishas\t\t\t\tlots'>

        >>> grid.delete(start=Coordinate(x=9, y=0), end=Coordinate(x=9, y=0))
        <TabExpandingTextGrid content='\t\t\t\tthishs\t\t\t\tlots'>

        >>> grid.delete(start=Coordinate(x=9, y=0), end=Coordinate(x=9, y=0))
        <TabExpandingTextGrid content='\t\t\t\tthish\t\t\t\tlots'>

        >>> grid.delete(start=Coordinate(x=9, y=0), end=Coordinate(x=9, y=0))
        <TabExpandingTextGrid content='\t\t\t\tthishlots'>

        """
        return super().delete(start=start, end=end)

    def get_tab_aligned_coordinate(self, *, coordinate):
        r"""Returns a coordinate that is aligned with the tabs.

        This is helpful for moving cursurs around to align them to the tabs.

        >>> grid = TabExpandingTextGrid(LinedTextGrid("I\thave\t\tlots of\ttabs"))
        >>> grid.get_tab_aligned_coordinate(coordinate=Coordinate(x=2, y=0))
        <Coordinate x=1, y=0>

        >>> grid.get_tab_aligned_coordinate(coordinate=Coordinate(x=16, y=0))
        <Coordinate x=13, y=0>

        >>> grid.get_tab_aligned_coordinate(coordinate=Coordinate(x=17, y=0))
        <Coordinate x=17, y=0>

        >>> grid.get_tab_aligned_coordinate(coordinate=Coordinate(x=18, y=0))
        <Coordinate x=18, y=0>

        >>> grid.get_tab_aligned_coordinate(coordinate=Coordinate(x=24, y=0))
        <Coordinate x=24, y=0>

        >>> grid.get_tab_aligned_coordinate(coordinate=Coordinate(x=25, y=0))
        <Coordinate x=24, y=0>
        """
        return super().get_tab_aligned_coordinate(coordinate=coordinate)

    def get_moved_coordinate(
        self,
        *,
        coordinate,
        new_x=None,
        new_y=None,
        up=0,
        down=0,
        left=0,
        right=0
    ):
        r"""
        >>> grid = TabExpandingTextGrid(LinedTextGrid("I\thave\t\tlots of\ttabs"))
        >>> start = Coordinate(x=0, y=0)
        >>> end = grid.get_moved_coordinate(coordinate=start, right=1)
        >>> end
        <Coordinate x=1, y=0>

        >>> end = grid.get_moved_coordinate(coordinate=end, right=1)
        >>> end
        <Coordinate x=5, y=0>

        >>> end = grid.get_moved_coordinate(coordinate=end, right=1)
        >>> end
        <Coordinate x=6, y=0>

        >>> end = grid.get_moved_coordinate(coordinate=end, right=2)
        >>> end
        <Coordinate x=8, y=0>

        >>> end = grid.get_moved_coordinate(coordinate=end, right=1)
        >>> end
        <Coordinate x=9, y=0>

        >>> end = grid.get_moved_coordinate(coordinate=end, right=1)
        >>> end
        <Coordinate x=13, y=0>

        >>> grid.get_moved_coordinate(coordinate=Coordinate(x=10, y=0))
        <Coordinate x=9, y=0>


        """
        return super().get_moved_coordinate(
            coordinate=coordinate,
            new_x=new_x,
            new_y=new_y,
            up=up,
            down=down,
            left=left,
            right=right,
        )

    def coordinate_is_after_content(self, *, coordinate):
        r"""Returns True if the coordinate is beyond the end of the text content

        >>> grid = TabExpandingTextGrid(LinedTextGrid("first\n\tsecond\n\tthird"))
        >>> grid.coordinate_is_after_content(coordinate=Coordinate(x=0, y=0))
        False
        >>> grid.coordinate_is_after_content(coordinate=Coordinate(x=10, y=0))
        False
        >>> grid.coordinate_is_after_content(coordinate=Coordinate(x=0, y=100))
        True
        >>> grid.coordinate_is_after_content(coordinate=Coordinate(x=7, y=2))
        False
        >>> grid.coordinate_is_after_content(coordinate=Coordinate(x=8, y=2))
        True

        """
        return super().coordinate_is_after_content(coordinate=coordinate)

    def search(self, *, needle, case_sensitive=True):
        r"""Search the text for the string contained in the needle parameter.

        Returns a list containing the the Coordiante of the starting positions
        where the string is found.

        >>> haystack = "the rain\nin west\tspain\nmainly\ndrains in the plain."
        >>> grid = TabExpandingTextGrid(LinedTextGrid(haystack))

        >>> grid.search(needle="goober")
        []

        >>> result = grid.search(needle="ain")
        >>> for item in result:
        ...    print(item)
        <Coordinate x=5, y=0>
        <Coordinate x=13, y=1>
        <Coordinate x=1, y=2>
        <Coordinate x=2, y=3>
        <Coordinate x=16, y=3>

        """
        return super().search(needle=needle, case_sensitive=case_sensitive)
