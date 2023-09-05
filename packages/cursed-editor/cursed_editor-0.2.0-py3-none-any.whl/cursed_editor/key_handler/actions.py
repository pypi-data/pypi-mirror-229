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

from .state import State


class BaseAction:
    name = "Unnamed Action"

    @staticmethod
    def perform(key, editor, state):
        raise NotImplementedError


class InsertKey(BaseAction):
    name = "Insert Character at Cursor Position"

    @staticmethod
    def perform(key, editor, state):
        editor.insert_before(key)
        return state


class MoveUp(BaseAction):
    name = "Move the Cursor Up"

    @staticmethod
    def perform(key, editor, state):
        multiplier = max(state.multiplier, 1)
        editor.move_cursor(up=multiplier)
        return State(state, multiplier=0)


class MoveDown(BaseAction):
    name = "Move the Cursor Down"

    @staticmethod
    def perform(key, editor, state):
        multiplier = max(state.multiplier, 1)
        editor.move_cursor(down=multiplier)
        return State(state, multiplier=0)


class MoveLeft(BaseAction):
    name = "Move the Cursor Left"

    @staticmethod
    def perform(key, editor, state):
        multiplier = max(state.multiplier, 1)
        editor.move_cursor(left=multiplier)
        return State(state, multiplier=0)


class MoveRight(BaseAction):
    name = "Move the Cursor Right"

    @staticmethod
    def perform(key, editor, state):
        multiplier = max(state.multiplier, 1)
        editor.move_cursor(right=multiplier)
        return State(state, multiplier=0)


class MoveToLine(BaseAction):
    name = "Move the Cursor to Specific Line"

    @staticmethod
    def perform(key, editor, state):
        multiplier = max(state.multiplier, 1)
        editor.move_cursor(y=multiplier)
        return State(state, multiplier=0)


class SwitchToInsertMode(BaseAction):
    name = "Switch to Insert Mode"

    @staticmethod
    def perform(key, editor, state):
        return State(state, mode="insert", multiplier=0)


class SwitchToInsertModeAfter(BaseAction):
    name = "Switch to Insert Mode After Cursor Position"

    @staticmethod
    def perform(key, editor, state):
        editor.move_cursor(right=1)
        return State(state, mode="insert", multiplier=0)


class SwitchToInsertModeAfterLine(BaseAction):
    name = "Switch to Insert Mode At the End of the Cursor Line"

    @staticmethod
    def perform(key, editor, state):
        editor.move_cursor(x=-1)
        return State(state, mode="insert", multiplier=0)


class SwitchToInsertModeStartLine(BaseAction):
    name = "Switch to Insert Mode At the Beginning of the Cursor Line"

    @staticmethod
    def perform(key, editor, state):
        editor.move_cursor(x=0)
        return State(state, mode="insert", multiplier=0)


class SwitchToCommandMode(BaseAction):
    name = "Switch to Command Mode"

    @staticmethod
    def perform(key, editor, state):
        return State(state, mode="command", multiplier=0)


class SwitchToSearchMode(BaseAction):
    name = "Switch to Case Sensitive Search Mode"

    @staticmethod
    def perform(key, editor, state):
        return State(
            state, mode="search", search_string="", case_sensitive_search=True
        )


class SwitchToCaseInsensitiveSearchMode(BaseAction):
    name = "Switch to Case Insensitive Search Mode"

    @staticmethod
    def perform(key, editor, state):
        return State(
            state, mode="search", search_string="", case_sensitive_search=False
        )


class Save(BaseAction):
    name = "Save File"

    @staticmethod
    def perform(key, editor, state):
        editor.save()
        return state


class Delete(BaseAction):
    name = "Deletes Character At Cursor Position"

    @staticmethod
    def perform(key, editor, state):
        multiplier = max(state.multiplier, 0)
        for _ in range(multiplier):
            editor.handle_delete()
        return State(state, multiplier=0)


class Backspace(BaseAction):
    name = "Deletes Character Preceeding Cursor Position"

    @staticmethod
    def perform(key, editor, state):
        editor.handle_backspace()
        return state


class Enter(BaseAction):
    name = "Inserts New Line at Cursor Position"

    @staticmethod
    def perform(key, editor, state):
        editor.handle_enter()
        return state


class AddKeyToMultiplier(BaseAction):
    name = "Add Key to Multiplier Number"

    @staticmethod
    def perform(key, editor, state):
        if key in "1234567890":
            multiplier = state.multiplier * 10 + int(key)
            state = State(state, multiplier=multiplier)
        return state


class JoinLines(BaseAction):
    name = "Combine the Current Line with the Following Line"

    @staticmethod
    def perform(key, editor, state):
        multiplier = max(state.multiplier, 1)
        for _ in range(multiplier):
            editor.move_cursor(x=-1)
            editor.handle_delete()
        return State(state, multiplier=0)


class SearchAddCharacter(BaseAction):
    name = "Add Character to Search String"

    @staticmethod
    def perform(key, editor, state):
        state = State(state, search_string=state.search_string + key)
        editor.incremental_search(
            search_string=state.search_string,
            mode="same",
            case_sensitive=state.case_sensitive_search,
        )
        return state


class SearchBackspace(BaseAction):
    name = "Remove Last Character from Search String"

    @staticmethod
    def perform(key, editor, state):
        state = State(state, search_string=state.search_string[:-1])
        return state


class FindNext(BaseAction):
    name = "Moves the Cursor to the Next Search Result"

    @staticmethod
    def perform(key, editor, state):
        editor.incremental_search(
            state.search_string, case_sensitive=state.case_sensitive_search
        )
        return state


class FindPrevious(BaseAction):
    name = "Moves the Cursor to the Previous Search Result"

    @staticmethod
    def perform(key, editor, state):
        editor.incremental_search(
            state.search_string,
            mode="reverse",
            case_sensitive=state.case_sensitive_search,
        )
        return state
