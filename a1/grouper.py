"""CSC148 Assignment 1

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Misha Schwartz, Mario Badr, Christine Murad, Diane Horton, Sophia Huynh
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) 2020 Misha Schwartz, Mario Badr, Christine Murad, Diane Horton,
Sophia Huynh and Jaisie Sin

=== Module Description ===

This file contains classes that define different algorithms for grouping
students according to chosen criteria and the group members' answers to survey
questions. This file also contain a classe that describes a group of students as
well as a grouping (a group of groups).
"""
from __future__ import annotations

import random
from typing import Any, List, TYPE_CHECKING

from course import sort_students

if TYPE_CHECKING:
    from survey import Survey
    from course import Course, Student


def slice_list(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing slices of <lst> in order. Each slice is a
    list of size <n> containing the next <n> elements in <lst>.

    The last slice may contain fewer than <n> elements in order to make sure
    that the returned list contains all elements in <lst>.

    === Precondition ===
    n <= len(lst)

    >>> slice_list([3, 4, 6, 2, 3], 2) == [[3, 4], [6, 2], [3]]
    True
    >>> slice_list(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [False]]
    True
    """
    new_list = []
    if n == 0:
        return []
    index = list(range(0, len(lst), n))
    for i in range(len(index)):
        if i < len(index):
            new_list.append(lst[index[i]:index[i] + n])
        elif 1 == len(index):
            new_list.append(lst[index[i]:])
    return new_list


def windows(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Return a list containing windows of <lst> in order. Each window is a list
    of size <n> containing the elements with index i through index i+<n> in the
    original list where i is the index of window in the returned list.

    === Precondition ===
    n <= len(lst)

    >>> windows([3, 4, 6, 2, 3], 2) == [[3, 4], [4, 6], [6, 2], [2, 3]]
    True
    >>> windows(['a', 1, 6.0, False], 3) == [['a', 1, 6.0], [1, 6.0, False]]
    True
    """
    new_list = []
    for i in range(len(lst)):
        if i + n <= len(lst):
            new_list.append(lst[i:i + n])
    return new_list


class Grouper:
    """
    An abstract class representing a grouper used to create a grouping of
    students according to their answers to a survey.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def __init__(self, group_size: int) -> None:
        """
        Initialize a grouper that creates groups of size <group_size>

        === Precondition ===
        group_size > 1
        """
        self.group_size = group_size

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """ Return a grouping for all students in <course> using the questions
        in <survey> to create the grouping.
        """
        raise NotImplementedError

    def _remove_from(self, target: List, elements: List) -> None:
        """Removes everything in elements from target
        === Representation Invariants ===
        all element in elements need to be in target
        """
        raise NotImplementedError

class AlphaGrouper(Grouper):
    """
    A grouper that groups students in a given course according to the
    alphabetical order of their names.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def _remove_from(self, target: List, elements: List) -> None:
        """Removes everything in elements from target
        === Representation Invariants ===
        all element in elements need to be in target
        """
        for element in elements:
            target.remove(element)

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        The first group should contain the students in <course> whose names come
        first when sorted alphabetically, the second group should contain the
        next students in that order, etc.

        All groups in this grouping should have exactly self.group_size members
        except for the last group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.

        Hint: the sort_students function might be useful
        """
        alpha_sorted = sort_students(course.get_students(), 'name')
        sliced_list = slice_list(alpha_sorted, self.group_size)
        grouping = Grouping()

        for lst in sliced_list:
            group = Group(lst)
            grouping.add_group(group)
        return grouping


class RandomGrouper(Grouper):
    """
    A grouper used to create a grouping of students by randomly assigning them
    to groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def _remove_from(self, target: List, elements: List) -> None:
        """Removes everything in elements from target
        === Representation Invariants ===
        all element in elements need to be in target
        """
        for element in elements:
            target.remove(element)

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Students should be assigned to groups randomly.

        All groups in this grouping should have exactly self.group_size members
        except for one group which may have fewer than self.group_size
        members if that is required to make sure all students in <course> are
        members of a group.
        """
        student = list(course.get_students())
        random.shuffle(student)
        sliced_list = slice_list(student, self.group_size)
        grouping = Grouping()
        for lst in sliced_list:
            group = Group(lst)
            grouping.add_group(group)
        return grouping


class GreedyGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a greedy algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def _remove_from(self, target: List, elements: List) -> None:
        """Removes everything in elements from target
        === Representation Invariants ===
        all element in elements need to be in target
        """
        for element in elements:
            target.remove(element)

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. select the first student in the tuple that hasn't already been put
           into a group and put this student in a new group.
        2. select the student in the tuple that hasn't already been put into a
           group that, if added to the new group, would increase the group's
           score the most (or reduce it the least), add that student to the new
           group.
        3. repeat step 2 until there are N students in the new group where N is
           equal to self.group_size.
        4. repeat steps 1-3 until all students have been placed in a group.

        In step 2 above, use the <survey>.score_students method to determine
        the score of each group of students.

        The final group created may have fewer than N members if that is
        required to make sure all students in <course> are members of a group.
        """
        all_student = list(course.get_students())
        student_count = len(all_student)
        grouping = Grouping()
        new_group = Group([])
        group_members = []
        best_candidate = 'dummy'
        while all_student:
            if (student_count - len(all_student)) % self.group_size == 0:
                student1 = all_student.pop(0)
                new_group = Group([student1])
                group_members = [student1]
            if self.group_size == 1:
                grouping.add_group(new_group)
                continue

            max_score = -100
            for student2 in all_student:
                test_group = new_group.get_members() + [student2]
                score = survey.score_students(test_group)
                if score > max_score:
                    max_score = score
                    best_candidate = student2
            if all_student:
                group_members.append(best_candidate)
                new_group = Group(group_members)
                all_student.remove(best_candidate)
            if len(new_group.get_members()) == self.group_size:
                grouping.add_group(new_group)
        if 0 < len(new_group) <= self.group_size:
            grouping.add_group(new_group)
        return grouping

class WindowGrouper(Grouper):
    """
    A grouper used to create a grouping of students according to their
    answers to a survey. This grouper uses a window search algorithm to create
    groups.

    === Public Attributes ===
    group_size: the ideal number of students that should be in each group

    === Representation Invariants ===
    group_size > 1
    """

    group_size: int

    def _remove_from(self, target: List, elements: List) -> None:
        """Removes everything in elements from target
        === Representation Invariants ===
        all element in elements need to be in target
        """
        for element in elements:
            target.remove(element)

    def make_grouping(self, course: Course, survey: Survey) -> Grouping:
        """
        Return a grouping for all students in <course>.

        Starting with a tuple of all students in <course> obtained by calling
        the <course>.get_students() method, create groups of students using the
        following algorithm:

        1. Get the windows of the list of students who have not already been
           put in a group.
        2. For each window in order, calculate the current window's score as
           well as the score of the next window in the list. If the current
           window's score is greater than or equal to the next window's score,
           make a group out of the students in current window and start again at
           step 1. If the current window is the last window, compare it to the
           first window instead.

        In step 2 above, use the <survey>.score_students to determine the score
        of each window (list of students).

        In step 1 and 2 above, use the windows function to get the windows of
        the list of students.

        If there are any remaining students who have not been put in a group
        after repeating steps 1 and 2 above, put the remaining students into a
        new group.
        """
        all_student = list(course.get_students())
        grouping = Grouping()
        while len(all_student) >= self.group_size:
            window_list = windows(all_student, self.group_size)
            for s in window_list:
                i = window_list.index(s)
                score = survey.score_students(window_list[i])
                if i == window_list.__len__() - 1:
                    next_score = survey.score_students(window_list[0])
                else:
                    next_score = survey.score_students(window_list[i + 1])
                if score >= next_score:
                    self._remove_from(all_student, window_list[i])
                    grouping.add_group(Group(window_list[i]))
                    break
        if all_student.__len__() > 0:
            grouping.add_group(Group(all_student))
        return grouping


class Group:
    """
    A group of one or more students

    === Private Attributes ===
    _members: a list of unique students in this group

    === Representation Invariants ===
    No two students in _members have the same id
    """

    _members: List[Student]

    def __init__(self, members: List[Student]) -> None:
        """ Initialize a group with members <members> """
        self._members = members

    def __len__(self) -> int:
        """ Return the number of members in this group """
        return len(self._members)

    def __contains__(self, member: Student) -> bool:
        """
        Return True iff this group contains a member with the same id
        as <member>.
        """
        for student in self._members:
            if student.id == member.id:
                return True
        return False

    def __str__(self) -> str:
        """
        Return a string containing the names of all members in this group
        on a single line.

        You can choose the precise format of this string.
        """
        names = []
        for member in self._members:
            names.append(member.name)
        return ', '.join(names)

    def get_members(self) -> List[Student]:
        """ Return a list of members in this group. This list should be a
        shallow copy of the self._members attribute.
        """
        return self._members[:]


class Grouping:
    """
    A collection of groups

    === Private Attributes ===
    _groups: a list of Groups

    === Representation Invariants ===
    No group in _groups contains zero members
    No student appears in more than one group in _groups
    """

    _groups: List[Group]

    def __init__(self) -> None:
        """ Initialize a Grouping that contains zero groups """
        self._groups = []

    def __len__(self) -> int:
        """ Return the number of groups in this grouping """
        return len(self._groups)

    def __str__(self) -> str:
        """
        Return a multi-line string that includes the names of all of the members
        of all of the groups in <self>. Each line should contain the names
        of members for a single group.

        You can choose the precise format of this string.
        """
        str_groups = ''
        for group in self._groups:
            str_groups += group.__str__() + '\n'
        return str_groups

    def add_group(self, group: Group) -> bool:
        """
        Add <group> to this grouping and return True.

        Iff adding <group> to this grouping would violate a representation
        invariant don't add it and return False instead.
        """
        if group.__len__() <= 0:
            return False
        for student in group.get_members():
            for a_group in self._groups:
                if student in a_group:
                    return False
        self._groups.append(group)
        return True

    def get_groups(self) -> List[Group]:
        """ Return a list of all groups in this grouping.
        This list should be a shallow copy of the self._groups
        attribute.
        """
        return self._groups[:]


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={'extra-imports': ['typing',
                                                  'random',
                                                  'survey',
                                                  'course']})
