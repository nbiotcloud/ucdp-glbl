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
Test Attr.
"""

import re

import ucdp as u
from pytest import raises

from ucdp_glbl.attrs import Attr, Attrs, cast_attrs


def test_attr():
    """Attr Without Value."""
    attr = Attr("one")
    assert attr.name == "one"
    assert attr.value is None


def test_attr_value():
    """Attr With Value."""
    attr = Attr("one", value="8k")
    assert attr.name == "one"
    assert attr.value == "8k"


def test_name():
    """Name."""
    with raises(u.ValidationError):
        Attr("1two")
    with raises(u.ValidationError):
        Attr("two1 f")
    with raises(u.ValidationError):
        Attr("two%")


def test_cast():
    """Casting."""
    assert cast_attrs("") == Attrs()
    assert cast_attrs("b") == (Attr("b"),)
    assert cast_attrs("b=1") == (Attr("b", value="1"),)
    assert cast_attrs("b=1;c") == (Attr("b", value="1"), Attr("c"))

    msg = "Duplicates in 'b=1; b=2'"
    with raises(ValueError, match=re.escape(msg)):
        cast_attrs("b=1;b=2")
