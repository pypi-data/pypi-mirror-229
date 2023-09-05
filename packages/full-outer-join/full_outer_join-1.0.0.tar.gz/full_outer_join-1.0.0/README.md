full\_outer\_join
===============

Lazy iterator implementations of a full outer join, inner join, 
and left and right joins of Python iterables.

This implements the [sort-merge join](https://en.wikipedia.org/wiki/Sort-merge_join),
better known as the merge join, to join iterables in O(n) time with respect to the length
of the longest iterable.

Note that the algorithm requires input to be sorted by the join key.

Example
-------
(whitespace to make things explicit)
```python
>>> list(full_outer_join.full_outer_join(
    [{"id": 1, "val": "foo"}                         ],
    [{"id": 1, "val": "bar"}, {"id": 2, "val": "baz"}],
    key=lambda x: x["id"]
))

[
    (1, ([{'id': 1, 'val': 'foo'}], [{'id': 1, 'val': 'bar'}])),
    (2, ([                       ], [{'id': 2, 'val': 'baz'}]))
]
```

To consume the output, your business logic might look like:

```python
for group_key, key_batches in full_outer_join.full_outer_join(left, right):
    left_rows, right_rows = key_batches
    
    if left_rows and right_rows:
        # This is the inner join case.
        pass
    elif left_rows and not right_rows:
        # This is the left join case (no matching right rows)
        pass
    elif not left_rows and right_rows:
        # This is the right join case (no matching left rows)
        pass
    elif not left_rows and not right_rows:
        raise Exception("Unreachable")
```

Functions
---------

| name                                                         | description                                                                                                                                                                                                                                                                      |
|--------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `full_outer_join(*iterables, key=lambda x: x)`               | Do a full outer join on any number of iterables, returning `(key, (list[row], ...))` for each key across all iterables.                                                                                                                                                          |
| `inner_join(*iterables, key=lambda x: x)`                    | Do an inner join across all iterables, returning `(key, (list[row], ...))` for keys only in all iterables                                                                                                                                                                        |
| `left_join(left_iterable, right_iterable, key=lambda x: x)`  | Do a left join on both iterables, returning keys for each unique key in `left_iterable`                                                                                                                                                                                          |
| `right_join(left_iterable, right_iterable, key=lambda x: x)` | Do a right join on both iterables, returning keys for each unique key in `right_iterable`                                                                                                                                                                                        |
| `cross_join(join_output, null=None)`                         | Do the cross (Cartesian) join on the output of `full_outer_join` or `inner_join`, yielding `(key, (iter1_row, ...))` for each row. This is implemented for completeness and is probably not useful. Iterables lacking any rows for `key` are replaced with `null` in the output. |


Why?
----

1. Your input is already sorted and you don't want to consume your input
   iterators.
2. Your business logic that consumes the joined output benefits from
   explicitly handling the match and no-match cases from each input
   iterable.
3. You're insane. Your brain is irreparably broken by the relational model. 


More examples
-------------

See test_insanity.py for a silly example of a SQL query hand-compiled into iterators.


Thanks
------
This was originally a PR to the [more_itertools](https://github.com/more-itertools/more-itertools) project
who gave some excellent feedback on the design but ultimately did not want to merge it in.