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


class MutableString(_private.MutableString):
    def __init__(self, content):
        """Initializes a MutableString object.
        >>> MutableString("the rain in spain")
        <MutableString content='the rain in spain'>
        """
        super().__init__(content)

    def __str__(self):
        """Returns the contents of the MutableString as a str
        >>> str(MutableString("a b c d e f g"))
        'a b c d e f g'
        """
        return super().__str__()

    def to_string(self):
        """Equivalent to str(self).  Helpful for method chaining.
        >>> MutableString("a b c d e f g").to_string()
        'a b c d e f g'
        """
        return super().to_string()

    def get_character_at(self, *, index):
        """Returns the character at the given index.

        >>> MutableString("a b c d e").get_character_at(index=4)
        'c'
        """
        return super().get_character_at(index=index)

    def insert_before(self, *, text, index):
        """Inserts the requested text before the given index.

        The text argument must be a str.
        The index argument must be an int.

        The provided index will be automatically bounded to be between 0 (zero)
        and the length of the underlying string minus 1 (one).

        As a result, this cannot be used to append text to the end of the
        string (for that, either the append and insert_after methods can be
        used)

        This method returns a reference to self to support method chaining.

        Examples:

        >>> MutableString("test bro").insert_before(text="neat ", index=0)
        <MutableString content='neat test bro'>

        >>> MutableString("test bro").insert_before(text="ing is neat", index=4)
        <MutableString content='testing is neat bro'>

        A TypeError is raised if the text parameter is not a string.

        >>> MutableString("test").insert_before(text=5, index=1)
        Traceback (most recent call last):
        TypeError: text parameter must be a str object

        Similarly, a TypeError is also raised if the index is not an int

        >>> MutableString("test").insert_before(text="bad", index="really bad")
        Traceback (most recent call last):
        TypeError: index parameter must be an int object

        If the provided index is less than zero, then we insert
        at the beginning of the string.

        >>> MutableString("test").insert_before(text="prepend ", index=-1)
        <MutableString content='prepend test'>

        If the provided index is greater than the length of the string,
        then the text is inserted before the last character of the string.

        >>> MutableString("end of .").insert_before(text="sentence", index=500)
        <MutableString content='end of sentence.'>
        """
        return super().insert_before(text=text, index=index)

    def insert_after(self, *, text, index):
        """Inserts the requested text after the given index.

        The text argument must be a string.
        The index argument must be an integer.

        The index will be automatically bounded to be between 0 (zero)
        and the length of the underlying string minus 1 (one).

        As a result, this cannot be used to prepend text to the beginning of
        the string (for that, either the insert_before or prepend methods can
        be used)

        This returns a reference to self to support method chaining.

        >>> MutableString("test bro").insert_after(text="ing is neat", index=3)
        <MutableString content='testing is neat bro'>

        >>> MutableString("test bro").insert_after(text="seph", index=7)
        <MutableString content='test broseph'>

        A TypeError is raised if the text parameter is not a string

        >>> MutableString("test").insert_after(text=5, index=1)
        Traceback (most recent call last):
        TypeError: text parameter must be a str object

        Similarly, a TypeError is also raised if the index is not an int

        >>> MutableString("test").insert_after(text="bad", index="really bad")
        Traceback (most recent call last):
        TypeError: index parameter must be an int object

        If the provided index is less than zero, then we insert after the
        first character in the string.

        >>> MutableString("Bro").insert_after(text=" cool b", index=-1)
        <MutableString content='B cool bro'>

        If the provided index is greater than the length of the string,
        then the text is appended to the end

        >>> MutableString("test").insert_after(text="ing is fun", index=500)
        <MutableString content='testing is fun'>
        """
        return super().insert_after(text=text, index=index)

    def append(self, *, text):
        """Appends the given text to the underlying text value.
        Return a reference to self to support method chaining.

        >>> MutableString("I eat").append(text=" red meat")
        <MutableString content='I eat red meat'>

        This will raise a TypeError if the text parameter is not a string

        >>> MutableString("seven eight").append(text=9)
        Traceback (most recent call last):
        TypeError: text parameter must be a str object
        """
        return super().append(text=text)

    def prepend(self, *, text):
        """Prepends the given text to the underlying text value.
        Return a reference to self to support method chaining.

        >>> MutableString("the greatest teacher").prepend(text="failure is ")
        <MutableString content='failure is the greatest teacher'>

        This will raise a TypeError if the text parameter is not a string

        >>> MutableString("seven eight").prepend(text=9)
        Traceback (most recent call last):
        TypeError: text parameter must be a str object
        """
        return super().prepend(text=text)

    def delete(self, *, start=0, end=None, length=None):
        """Deletes the text between the given indices (inclusively).

        >>> MutableString("I am funny and smart").delete(start=8, end=9)
        <MutableString content='I am fun and smart'>

        >>> MutableString("I am funny, and smart").delete(start=10, end=10)
        <MutableString content='I am funny and smart'>

        >>> MutableString("").delete(start=8, end=9)
        <MutableString content=''>

        Instead of providing the end parameter, passing a length is also
        acceptable.

        >>> MutableString("I am funny and smart").delete(start=8, length=2)
        <MutableString content='I am fun and smart'>

        >>> MutableString("I am funny, and smart").delete(start=10, length=1)
        <MutableString content='I am funny and smart'>

        Passing length=0 results in no change to the string

        >>> MutableString("I am funny and smart").delete(start=5, length=0)
        <MutableString content='I am funny and smart'>

        But length has to be at least zero.

        >>> MutableString("I am funny and smart").delete(start=5, length=-1)
        Traceback (most recent call last):
        ValueError: length parameter must be at least zero

        Passing start by itself removes all trailing text from the string.

        >>> MutableString("I am funny, and smart").delete(start=8)
        <MutableString content='I am fun'>

        The starting index actually used is the requested starting index
        modulo the length of the string, so negative numbers are allowed.

        >>> MutableString("I am funny and smart").delete(start=-10)
        <MutableString content='I am funny'>

        >>> MutableString("I am funny, and smart").delete(start=-11, end=10)
        <MutableString content='I am funny and smart'>

        This lets you use rather crazy values for the starting index.

        >>> assert 1900 % 21 == 10
        >>> MutableString("I am funny, and smart").delete(start=1900)
        <MutableString content='I am funny'>

        Note that the ending index we use is also the requested ending index
        moduleo the length of hte string.

        >>> MutableString("I am funny, and smart").delete(start=-11, end=-11)
        <MutableString content='I am funny and smart'>

        >>> MutableString("I am funny, and smart").delete(start=-11, end=1900)
        <MutableString content='I am funny and smart'>

        However, The start parameter is optional and defaults to 0 (zero).

        >>> MutableString("I am funny and smart").delete(end=14)
        <MutableString content='smart'>

        Passing length by itself also works.

        >>> MutableString("I am funny and smart").delete(length=15)
        <MutableString content='smart'>

        By now you may have noticed that end = start + length - 1.
        This is because I wanted "end" to be inclusive, which is
        contrary to how slicing normally works in python.

        As a result, passing length=0 results in no change to the string

        >>> MutableString("I am funny and smart").delete(start=5, length=0)
        <MutableString content='I am funny and smart'>

        To truncate the entire string, simply call delete without any arguments.

        >>> MutableString("I am funny and smart").delete()
        <MutableString content=''>

        Naturally, start, end, and length, if provided must all be int objects.

        >>> MutableString("Well shucks").delete(start="moose")
        Traceback (most recent call last):
        TypeError: start parameter must be an int object

        >>> MutableString("Well shucks").delete(end="")
        Traceback (most recent call last):
        TypeError: end parameter must be an int object

        >>> MutableString("Well shucks").delete(length="moose")
        Traceback (most recent call last):
        TypeError: length parameter must be an int object


        Also, end and length cannot both be specified simultaneously

        >>> MutableString("I am funny and smart").delete(start=5, end=7, length=4)
        Traceback (most recent call last):
        ValueError: cannot pass values for both end and length parameters

        Also, the end cannot be less than the start

        >>> MutableString("I am funny and smart").delete(start=5, end=3)
        Traceback (most recent call last):
        ValueError: the end must be greater than the start


        Tired of hearing how funny and smart I am?   So is my wife hahaha.
        """
        return super().delete(start=start, end=end, length=length)

    def search(self, *, needle, case_sensitive=True):
        r"""Search the text for the string contained in the needle parameter.

        Returns a list containing the the starting positions where the string
        is found.

        >>> haystack = "the rain\nin west\tspain\nmainly\ndrains in the plain."
        >>> mut = MutableString(haystack)

        >>> mut.search(needle="ain")
        [5, 19, 24, 32, 46]

        >>> mut.search(needle="goober")
        []

        """
        return super().search(needle=needle, case_sensitive=case_sensitive)
