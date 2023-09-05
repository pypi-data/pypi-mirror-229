from itertools import groupby, count, product
from heapq import merge
from operator import itemgetter


_unwrapping_keyfunc = itemgetter(0)


def full_outer_join(*iterables, key=lambda x: x):
    """Lazily yields a full outer join of all iterables. The iterables are
    expected to be sorted. Uses the merge join algorithm which runs in O(n)
    time. Avoids buffering an entire iterable into memory.

    The default key function is an identity function.

        >>> left_rows = [{"id": 1, "val": "foo"}]
        >>> right_rows = [{"id": 1, "val": "bar"}, {"id": 2, "val": "baz"}]
        >>> list(full_outer_join(left_rows, right_rows, key=lambda x: x["id"]))
        [(1, ([{'id': 1, 'val': 'foo'}], [{'id': 1, 'val': 'bar'}])), \
(2, ([], [{'id': 2, 'val': 'baz'}]))]
    """

    def _augment_iterable(idx, iterable):
        for item in iterable:
            yield key(item), idx, item

    augmented_iterables = map(_augment_iterable, count(), iterables)

    for group_key, group in groupby(
        merge(*augmented_iterables, key=_unwrapping_keyfunc),
        key=_unwrapping_keyfunc,
    ):
        key_batches = tuple([] for _ in iterables)
        for _, augment_idx, value in group:
            key_batches[augment_idx].append(value)
        yield group_key, key_batches


def inner_join(*iterables, key=lambda x: x):
    """Lazily yields an inner join of all iterables. The iterables are
    expected to be sorted. Uses the merge join algorithm which runs in O(n)
    time. Avoids buffering an entire iterable into memory.

    The default key function is an identity function.

        >>> left_rows = [{"id": 1, "val": "foo"}]
        >>> right_rows = [{"id": 1, "val": "bar"}, {"id": 2, "val": "baz"}]
        >>> list(inner_join(left_rows, right_rows, key=lambda x: x["id"]))
        [(1, ([{'id': 1, 'val': 'foo'}], [{'id': 1, 'val': 'bar'}]))]
    """
    for group_key, key_batches in full_outer_join(*iterables, key=key):
        if any(not key_batch for key_batch in key_batches):
            continue
        yield group_key, key_batches


_left_batch = itemgetter(0)
_right_batch = itemgetter(1)


def _left_right_join(
    _batch_getter, left_iterable, right_iterable, key=lambda x: x
):
    for group_key, key_batches in full_outer_join(
        left_iterable, right_iterable, key=key
    ):
        if not _batch_getter(key_batches):
            continue
        yield group_key, key_batches


def left_join(left_iterable, right_iterable, key=lambda x: x):
    """Lazily yields a left join on the left_iterable. The iterables are
    expected to be sorted. Uses the merge join algorithm which runs in O(n)
    time. Avoids buffering an entire iterable into memory.

    The default key function is an identity function.

        >>> left_rows = [{"id": 1, "val": "foo"}]
        >>> right_rows = [{"id": 1, "val": "bar"}, {"id": 2, "val": "baz"}]
        >>> list(inner_join(left_rows, right_rows, key=lambda x: x["id"]))
        [(1, ([{'id': 1, 'val': 'foo'}], []))]
    """
    for group_key, key_batches in _left_right_join(
        _left_batch, left_iterable, right_iterable, key=key
    ):
        yield group_key, key_batches


def right_join(left_iterable, right_iterable, key=lambda x: x):
    """Lazily yields a right join on the left_iterable. The iterables are
    expected to be sorted. Uses the merge join algorithm which runs in O(n)
    time. Avoids buffering an entire iterable into memory.

    The default key function is an identity function.

        >>> left_rows = [{"id": 1, "val": "foo"}]
        >>> right_rows = [{"id": 1, "val": "bar"}, {"id": 2, "val": "baz"}]
        >>> list(inner_join(left_rows, right_rows, key=lambda x: x["id"]))
        [(1, ([{'id': 1, 'val': 'foo'}], [{'id': 1, 'val': 'bar'}])), \
(2, ([], [{'id': 2, 'val': 'baz'}]))]
    """
    for group_key, key_batches in _left_right_join(
        _right_batch, left_iterable, right_iterable, key=key
    ):
        yield group_key, key_batches


def cross_join(join_output, null=None):
    """Transform the (group_key, key_batches) output of one of the other
    joins into a (group_key, row) format.

    The value of null, default None, is used as a placeholder for any iterable
    missing values in that key batch."""
    for group_key, key_batches in join_output:
        yield from (
            (group_key, row)
            for row in product(
                *(batch if batch else [null] for batch in key_batches)
            )
        )
