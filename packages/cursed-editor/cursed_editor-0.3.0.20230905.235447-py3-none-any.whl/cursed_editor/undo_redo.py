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

logger = logging.getLogger(__name__)


class FirstEvent:
    def __init__(self):
        self.next = None

    def __repr__(self):
        return "<FirstEvent>"


class Insertion:
    def __init__(self, *, position, text):
        self.position = position
        self.text = text
        self.next = None
        self.previous = None

    def __repr__(self):
        return f"<Insertion position={self.position} text='{self.text}'>"


class Deletion:
    def __init__(self, *, position, text):
        self.position = position
        self.text = text
        self.next = None
        self.previous = None

    def __repr__(self):
        return f"<Deletion position={self.position} text='{self.text}'>"


class UndoRedo:
    def __init__(self):
        self.last_event = FirstEvent()

    def add_insertion_event(self, *, position, text):
        new = Insertion(position=position, text=text)
        self._add_event(new)

    def add_deletion_event(self, *, position, text):
        new = Deletion(position=position, text=text)
        self._add_event(new)

    def _add_event(self, new):
        logger.info(f"adding event {new}")
        self.last_event.next = new
        new.previous = self.last_event
        self.last_event = new

    def undo(self, editor):
        logger.info(f"undoing event: {self.last_event}")
        if isinstance(self.last_event, Insertion):
            self._apply_delete(self.last_event, editor)
        elif isinstance(self.last_event, Deletion):
            self._apply_insert(self.last_event, editor)
        if not isinstance(self.last_event, FirstEvent):
            self.last_event = self.last_event.previous

    def _apply_delete(self, event, editor):
        position = event.position
        editor.move_cursor(x=position.x, y=position.y)
        editor.handle_delete(add_event=False)

    def _apply_insert(self, event, editor):
        position = event.position
        editor.move_cursor(x=position.x, y=position.y)
        editor.insert(self.last_event.text, add_event=False)

    def redo(self, editor):
        event = self.last_event
        if self.last_event.next is None:
            logger.info("nothing to redo")
        else:
            self.last_event = self.last_event.next
            logger.info(f"redoing event: {event}")
            if isinstance(self.last_event, Insertion):
                self._apply_insert(self.last_event, editor)
            else:
                self._apply_delete(self.last_event, editor)
