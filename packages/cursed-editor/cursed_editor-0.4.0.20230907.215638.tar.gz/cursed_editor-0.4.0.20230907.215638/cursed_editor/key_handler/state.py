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


class State:
    def __init__(self, state=None, **kwargs):
        args = {}
        if state is not None:
            args.update(state.__dict__)
        args.update(kwargs)
        self.multiplier = args.get("multiplier", 0)
        self.mode = args.get("mode", "command")
        self.search_string = args.get("search_string", "")
        self.case_sensitive_search = args.get("case_sensitive_search", True)
        self._is_setup = True

    def __setattr__(self, key, value):
        if hasattr(self, "_is_setup"):
            raise TypeError("can't modify state")
        super().__setattr__(key, value)
