from typing import Callable, Iterable, Iterator, TypeVar

import sys

if sys.version_info >= (3, 11):
    from typing import Unpack, TypeAlias
else:
    from typing_extensions import Unpack, TypeAlias

_T = TypeVar('_T')
_U = TypeVar('_U')
_V = TypeVar('_V')

_relation_type: TypeAlias = Iterable[_T]
_keyfunc_type: TypeAlias = Callable[[_T], _U]
_join_result_type: TypeAlias = Iterator[tuple[_U, tuple[list[_T]]]]

def full_outer_join(
    *iterables: _relation_type[_T], key: _keyfunc_type[_T, _U] = ...
) -> _join_result_type[_T, _U]: ...
def inner_join(
    *iterables: _relation_type[_T], key: _keyfunc_type[_T, _U] = ...
) -> _join_result_type[_T, _U]: ...
def left_join(
    left_iterable: _relation_type[_T],
    right_iterable: _relation_type[_T],
    key: _keyfunc_type[_T, _U] = ...,
) -> _join_result_type[_T, _U]: ...
def right_join(
    left_iterable: _relation_type[_T],
    right_iterable: _relation_type[_T],
    key: _keyfunc_type[_T, _U] = ...,
) -> _join_result_type[_T, _U]: ...
def cross_join(
    join_output: _join_result_type[_T, _U], null: _V = ...
) -> Iterator[tuple[_U, Unpack[tuple[_T, _V]]]]: ...
