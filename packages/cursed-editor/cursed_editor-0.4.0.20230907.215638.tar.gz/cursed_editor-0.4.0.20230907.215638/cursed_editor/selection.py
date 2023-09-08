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


def linear(*, text, start, end, line_break="\n"):
    lines = list(x + line_break for x in text.split(line_break))
    lines[-1] = lines[-1].split(line_break)[0]
    if start.y < 0:
        start_y = 0
        start_x = 0
    else:
        start_y = start.y
        start_x = max(start.x, 0)
    if start_y >= len(lines):
        return ""
    if end.y < start_y:
        return ""
    if end.y == start_y:
        if end.x < start_x:
            return ""
        line = lines[start_y]
        if start_x >= len(line):
            return ""
        return line[start_x : end.x + 1]
    selected_lines = lines[start_y : end.y + 1]
    selected_lines[0] = selected_lines[0][start_x:]
    if end.y >= len(lines):
        pass
    elif end.x < 0:
        selected_lines[-1] = ""
    else:
        selected_lines[-1] = selected_lines[-1][: end.x + 1]
    result = "".join(selected_lines)
    return result


def before(*, text, coordinate, line_break="\n"):
    if coordinate.y < 0:
        return ""
    if coordinate.y == 0 and coordinate.x <= 0:
        return ""
    lines = list(x + line_break for x in text.split(line_break))
    lines[-1] = lines[-1].split(line_break)[0]
    if coordinate.y > len(lines):
        return text
    lines = lines[: coordinate.y + 1]
    x = max(coordinate.x, 0)
    lines[-1] = lines[-1][:x]
    result = "".join(lines)
    return result


def after(*, text, coordinate, line_break="\n"):
    if coordinate.y < 0:
        return text
    if coordinate.y == 0 and coordinate.x < 0:
        return text
    lines = list(x + line_break for x in text.split(line_break))
    lines[-1] = lines[-1].split(line_break)[0]
    if coordinate.y > len(lines):
        return ""
    lines = lines[coordinate.y :]
    lines[0] = lines[0][coordinate.x + 1 :]
    result = "".join(lines)
    return result


def except_linear(*, text, start, end, line_break="\n"):
    if start > end:
        return text
    before_text = before(text=text, coordinate=start, line_break=line_break)
    after_text = after(text=text, coordinate=end, line_break=line_break)
    return before_text + after_text


def text_lines(*, text, line_ending, start, end):
    full_lines = text.split(line_ending)
    if start is None:
        start = 0
    if not isinstance(start, int):
        raise TypeError("start parameter must be either None or an int")
    start = min(max(start, 0), len(full_lines) - 1)
    if end is None:
        end = len(full_lines) - 1
    if not isinstance(end, int):
        raise TypeError("end parameter must be either None or an int")
    end = min(max(end, 0), len(full_lines) - 1)
    if end < start:
        raise ValueError("end must be greater than start")
    end = end + 1
    return full_lines[slice(start, end)]
