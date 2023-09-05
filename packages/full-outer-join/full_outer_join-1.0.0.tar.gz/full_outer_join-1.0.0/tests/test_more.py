from unittest import TestCase

from full_outer_join import (
    full_outer_join,
    inner_join,
    left_join,
    right_join,
    cross_join,
)


class FullOuterJoinTests(TestCase):
    def test_empty(self):
        result = list(full_outer_join([], []))
        expected = []
        self.assertEqual(result, expected)

    def test_all_match(self):
        i1 = [1, 2]
        i2 = [1, 2]

        result = list(full_outer_join(i1, i2))
        expected = [(1, ([1], [1])), (2, ([2], [2]))]
        self.assertEqual(result, expected)

    def test_not_match(self):
        i1 = [1, 2]
        i2 = [1, 2]
        i3 = [1, 3]

        result = list(full_outer_join(i1, i2, i3))
        expected = [
            (1, ([1], [1], [1])),
            (2, ([2], [2], [])),
            (3, ([], [], [3])),
        ]
        self.assertEqual(result, expected)

    def test_many_iterables(self):
        i1 = [1, 3]
        i2 = [1, 4]
        i3 = [1, 5]
        i4 = [1, 6]

        result = list(full_outer_join(i1, i2, i3, i4))
        expected = [
            (1, ([1], [1], [1], [1])),
            (3, ([3], [], [], [])),
            (4, ([], [4], [], [])),
            (5, ([], [], [5], [])),
            (6, ([], [], [], [6])),
        ]
        self.assertEqual(result, expected)

    def test_inner_join(self):
        i1 = [1, 2]
        i2 = [2]

        result = list(inner_join(i1, i2))
        expected = [
            (2, ([2], [2])),
        ]
        self.assertEqual(result, expected)

    def test_left_join(self):
        i1 = [1, 2]
        i2 = [2]

        result = list(left_join(i1, i2))
        expected = [
            (1, ([1], [])),
            (2, ([2], [2])),
        ]
        self.assertEqual(result, expected)

    def test_right_join(self):
        i1 = [1, 2]
        i2 = [2, 3]

        result = list(right_join(i1, i2))
        expected = [
            (2, ([2], [2])),
            (3, ([], [3])),
        ]
        self.assertEqual(result, expected)

    def test_cross_join(self):
        null = object()
        obj1 = 'xxx'
        obj2 = 'yyy'
        obj3 = 'zzz'

        join_output = [(1, ([], [obj1], [obj2, obj3]))]
        result = list(cross_join(join_output, null=null))
        expected = [
            (1, (null, obj1, obj2)),
            (1, (null, obj1, obj3)),
        ]
        self.assertEqual(result, expected)
