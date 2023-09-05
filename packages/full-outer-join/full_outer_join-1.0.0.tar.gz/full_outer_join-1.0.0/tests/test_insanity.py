import statistics
from functools import partial
from unittest import TestCase
from itertools import groupby

from full_outer_join import left_join


class InsanityTests(TestCase):
    # My query-building logic is not very thought out,
    # please don't let this inspire you.

    def test_dog_visits(self):
        # CREATE TABLE dogs (dog_id INT, dog_name TEXT, dog_color TEXT);
        dogs = [
            {"dog_id": 1, "dog_name": "Snowball", "dog_color": "red"},
            {"dog_id": 2, "dog_name": "Blake", "dog_color": "green"},
            {"dog_id": 3, "dog_name": "Izzy", "dog_color": "blue"},
        ]

        # CREATE TABLE dog_visits (
        #   dog_visit_id INT, dog_id INT, dog_weight INT
        # );
        dog_visits = [
            # mean weight of 10
            {"dog_visit_id": 1, "dog_id": 1, "dog_weight": 5},
            {"dog_visit_id": 2, "dog_id": 1, "dog_weight": 10},
            {"dog_visit_id": 3, "dog_id": 1, "dog_weight": 15},
            # mean weight of 55
            {"dog_visit_id": 4, "dog_id": 2, "dog_weight": 50},
            {"dog_visit_id": 5, "dog_id": 2, "dog_weight": 60},
            # no visits for dog #3
        ]

        def _keyfunc(row):
            return row["dog_id"]

        def _id(iterable_idx, name, rows):
            return {name: rows[iterable_idx][0][name]}

        def _avg(iterable_idx, name, rows):
            return {
                name: statistics.mean(
                    row["dog_weight"] for row in rows[iterable_idx]
                )
                if rows[iterable_idx]
                else None
            }

        def _count(iterable_idx, name, rows):
            return {name: len(rows[iterable_idx])}

        def _select(groupby_rows, *select_fns):
            for _, group in groupby_rows:
                key_batches = list(group)[0][1]
                new_row = {}
                [
                    new_row.update(select_fn(key_batches))
                    for select_fn in select_fns
                ]
                yield new_row

        # SELECT
        #     dog_id,
        #     dog_name,
        #     avg(dog_weight) AS avg_dog_weight,
        #     count(*) AS dog_visits
        # FROM dogs
        # LEFT JOIN dog_visits ON dogs.dog_id = dog_visits.dog_id
        # GROUP BY dog_id

        result = list(
            _select(
                groupby(
                    left_join(dogs, dog_visits, key=_keyfunc),
                    key=lambda row: row[0],
                ),
                partial(_id, 0, "dog_id"),
                partial(_id, 0, "dog_name"),
                partial(_avg, 1, "dog_weight"),
                partial(_count, 1, "dog_visits"),
            )
        )

        # Wow, that was better than SQL!

        expected = [
            {
                'dog_id': 1,
                'dog_name': 'Snowball',
                'dog_visits': 3,
                'dog_weight': 10,
            },
            {
                'dog_id': 2,
                'dog_name': 'Blake',
                'dog_visits': 2,
                'dog_weight': 55,
            },
            {
                'dog_id': 3,
                'dog_name': 'Izzy',
                'dog_visits': 0,
                'dog_weight': None,
            },
        ]
        self.assertEqual(result, expected)
