#
# MIT License
#
# Copyright (c) 2024-2025 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""
Generic Attributes.

These are handy and type save key-value-pairs.

    >>> cast_attrs({'a': '1', 'b': '2'})
    (Attr('a', value='1'), Attr('b', value='2'))
    >>> cast_attrs(("a=1", "b=2"))
    (Attr('a', value='1'), Attr('b', value='2'))
    >>> cast_attrs("a=1; b=2")
    (Attr('a', value='1'), Attr('b', value='2'))
    >>> as_dict(cast_attrs("a=1; b=2"))
    {'a': '1', 'b': '2'}
    >>> as_tuple(cast_attrs("a=1; b=2"))
    (('a', '1'), ('b', '2'))
"""

from typing import Annotated, TypeAlias, Union

import ucdp as u
from pydantic import (
    BeforeValidator,
)


class Attr(u.IdentLightObject):
    """
    Attribute.

    Immutable Key-Value Pair.
    """

    value: str | None = None

    _posargs: u.ClassVar[u.PosArgs] = ("name",)

    def __init__(self, name: str, value: str | None = None) -> None:
        super().__init__(name=name, value=value)

    def __str__(self) -> str:
        if self.value is None:
            return self.name
        return f"{self.name}={self.value}"

    @staticmethod
    def cast(attr: Union["Attr", str]) -> "Attr":
        """
        Cast To Attribute.

            >>> Attr.cast(Attr('one'))
            Attr('one')
            >>> Attr.cast("one")
            Attr('one')
            >>> Attr.cast("one=2")
            Attr('one', value='2')

        """
        if isinstance(attr, Attr):
            return attr
        if "=" in attr:
            name, value = attr.split("=", 1)
            return Attr(name=name, value=value)
        return Attr(name=attr)


Attrs: TypeAlias = tuple[Attr, ...]


def cast_attrs(attrs: Union["Attrs", u.Names, dict, None]) -> "Attrs":
    """
    Cast To Attributes.

        >>> cast_attrs({'a': '1', 'b': '2'})
        (Attr('a', value='1'), Attr('b', value='2'))
        >>> cast_attrs(("a=1", "b=2"))
        (Attr('a', value='1'), Attr('b', value='2'))
        >>> cast_attrs("a=1; b=2")
        (Attr('a', value='1'), Attr('b', value='2'))
        >>> cast_attrs("")
        ()
        >>> cast_attrs(None)
        ()
    """
    if not attrs:
        return ()
    if isinstance(attrs, dict):
        attrs = tuple(Attr(name, value=value) for name, value in attrs.items())
    if not isinstance(attrs, tuple) or not all(isinstance(attr, Attr) for attr in attrs):
        attrs = tuple(Attr.cast(attr) for attr in u.split(attrs))
    # check for duplicates
    if len(set(dict(attrs))) != len(attrs):
        raise ValueError(f"Duplicates in {as_str(attrs)!r}")
    return attrs


def as_str(attrs: Attrs) -> str:
    """
    Return Attributes As String.

        >>> attrs = (Attr('a', value='1'), Attr('b'))
        >>> as_str(attrs)
        'a=1; b'

    """
    return "; ".join(str(attr) for attr in attrs)


format_attrs = as_str


def as_dict(attrs: Attrs) -> dict[str, str | None]:
    """Return Attributes As Dictionary."""
    return {attr.name: attr.value for attr in attrs}


def as_tuple(attrs: Attrs) -> tuple[tuple[str, str | None], ...]:
    """Return Attributes As Tuple."""
    return tuple((attr.name, attr.value) for attr in attrs)


CastableAttrs = Annotated[
    Attrs,
    BeforeValidator(lambda x: cast_attrs(x)),
]
