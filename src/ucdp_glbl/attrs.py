#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
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
Attributes.
"""

from typing import Annotated, TypeAlias

import ucdp as u
from pydantic import (
    BeforeValidator,
)

Attr: TypeAlias = tuple[str, str]
Attrs: TypeAlias = tuple[Attr, ...]


def cast_attrs(attrs: Attrs | u.Names | None) -> Attrs:
    """
    Cast Attributes.

    >>> cast_attrs({'a': '1', 'b': '2'})
    (('a', '1'), ('b', '2'))
    >>> cast_attrs((('a', '1'), ('b', '2')))
    (('a', '1'), ('b', '2'))
    >>> cast_attrs(("a=1", "b=2"))
    (('a', '1'), ('b', '2'))
    >>> cast_attrs("a=1; b=2")
    (('a', '1'), ('b', '2'))
    >>> cast_attrs("")
    ()
    >>> cast_attrs(None)
    ()
    >>> cast_attrs((('a', '1'), ('b', '2', 'toomuch')))
    Traceback (most recent call last):
        ...
    ValueError: Invalid Attr ('b', '2', 'toomuch')
    """
    if not attrs:
        return ()
    if isinstance(attrs, dict):
        return tuple(attrs.items())
    return tuple(cast_attr(attr) for attr in u.split(attrs))


def cast_attr(attr: Attr | str) -> Attr:
    """
    Cast Attribute.
    """
    if isinstance(attr, str):
        return tuple(attr.split("=", 1)) if "=" in attr else (attr, "")  # type: ignore[return-value]
    if isinstance(attr, tuple) and len(attr) == 2:  # noqa: PLR2004
        return attr
    raise ValueError(f"Invalid Attr {attr}")


CastableAttrs = Annotated[
    Attrs,
    BeforeValidator(lambda x: cast_attrs(x)),
]
