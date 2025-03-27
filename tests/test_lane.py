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
Test Lanes.
"""

from ucdp_glbl.attrs import Attr, Attrs
from ucdp_glbl.lane import Lane


def test_lane():
    """Lane Basics."""
    lane = Lane(name="one", size="8k")
    assert lane.name == "one"
    assert lane.size == 8 * 1024
    assert lane.attrs == Attrs()

    assert hash(lane)


def test_lane_attrs():
    """Lane Attributes."""
    assert Lane(name="a", size=1, attrs="").attrs == Attrs()
    assert Lane(name="a", size=1, attrs="b").attrs == (Attr("b"),)
    assert Lane(name="a", size=1, attrs="b=1").attrs == (Attr("b", value="1"),)
    assert Lane(name="a", size=1, attrs="b=1;c").attrs == (Attr("b", value="1"), Attr("c"))
