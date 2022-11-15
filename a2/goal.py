"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    goals = []
    a = random.randint(0, 1)
    colours = COLOUR_LIST[:]
    for _ in range(num_goals):
        colour = random.randint(0, len(colours) - 1)
        if a == 0:
            goal = PerimeterGoal(colours[colour])
        else:
            goal = BlobGoal(colours[colour])
        goals.append(goal)
        colours.pop(colour)
    return goals


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    if len(block.children) == 0:
        lst = []
        for _ in range(2 ** (block.max_depth - block.level)):
            col = []
            for _ in range(2 ** (block.max_depth - block.level)):
                col.append(block.colour)

            lst.append(col)

        return lst

    else:
        c1_f, c2_f, c3_f, c4_f = _flatten(block.children[0]), \
                                 _flatten(block.children[1]), \
                                 _flatten(block.children[2]), \
                                 _flatten(block.children[3])
        for i in range(len(c2_f)):
            c2_f[i].extend(c3_f[i])
            c1_f[i].extend(c4_f[i])

        c2_f.extend(c1_f)

        return c2_f


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A type of Goal which a player must aim to have as many
    given-colour unit cells that are touching the outer perimeter
    as possible.
    The score is calculated by counting the total length of all unit cells
    that have the given colour and are touching the outer perimeter.
    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        matrix = _flatten(board)
        s = 0
        colour = self.colour
        for i in range(len(matrix)):
            if colour == matrix[i][0]:
                s += 1
            if colour == matrix[0][i]:
                s += 1
            if colour == matrix[-1][i]:
                s += 1
            if colour == matrix[i][-1]:
                s += 1
        return s


    def description(self) -> str:
        a = 'aim to put the most possible units of the '
        b = colour_name(self.colour)
        c = 'on the outer perimeter of the board.'
        return a + b + ' ' + c


class BlobGoal(Goal):
    """A type of Goal which a player must aim to form the largest
    blob of the given colour.
    A blob is a group of connected blocks. Blocks are connected if they share
    the same edge; blocks with touching corners are not connected.
    The score of a player is calculating by adding the total unit cells
    of the given colour and form the largest blob.
    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        matrix = _flatten(board)
        l = len(matrix)
        visited = [[-1 for i in range(l)] for j in range(l)]
        return max(self._undiscovered_blob_size((i, j), matrix, visited) \
                   for i in range(l) for j in range(l))

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        if pos[0] < 0 or pos[0] > (len(visited) - 1) \
                or pos[1] < 0 or pos[1] > (len(visited) - 1):
            return 0

        if visited[pos[0]][pos[1]] == 0 or visited[pos[0]][pos[1]] == 1:
            return 0

        if board[pos[0]][pos[1]] != self.colour:
            visited[pos[0]][pos[1]] = 0
            return 0

        else:
            visited[pos[0]][pos[1]] = 1

            return 1 + self._undiscovered_blob_size(
                (pos[0], pos[1] - 1), board, visited)\
                   + self._undiscovered_blob_size(
                       (pos[0], pos[1] + 1), board, visited)\
                          + self._undiscovered_blob_size(
                              (pos[0] - 1, pos[1]), board, visited)\
                                  + self._undiscovered_blob_size(
                                      (pos[0] + 1, pos[1]), board, visited)

    def description(self) -> str:
        a = 'Aim for the largest blob of the '
        b = colour_name(self.colour)

        return a + b + '.'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
