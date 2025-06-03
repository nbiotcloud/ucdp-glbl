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
Generic Lanes.

A lane is anything which is related to any size and optionally additional attributes.
"""

from typing import TypeAlias

import ucdp as u

from .attrs import CastableAttrs


class Lane(u.IdentLightObject):
    """Lane."""

    size: u.Bytesize | None = None
    """Size in Bytes."""

    attrs: CastableAttrs = u.Field(default_factory=dict)
    """Attributes."""


class DefaultLane(Lane):
    """Default Lane."""

    name: str = u.Field(init=False, default="")


Lanes: TypeAlias = tuple[Lane, ...]


def fill_lanes(lanes: Lanes, size: u.Bytesize, default: bool = False) -> Lanes:
    """
    Fill Empty Lane Sizes.

        >>> fill_lanes((Lane(name='a'), Lane(name='b')), u.Bytesize('48kB'))
        (Lane(name='a', size=Bytesize('24 KB')), Lane(name='b', size=Bytesize('24 KB')))
        >>> fill_lanes((Lane(name='a', size='24k'), Lane(name='b', size='24k')), u.Bytesize('48kB'))
        (Lane(name='a', size=Bytesize('24 KB')), Lane(name='b', size=Bytesize('24 KB')))

        >>> fill_lanes((Lane(name='a', size='48k'), Lane(name='b')), u.Bytesize('48kB'))
        Traceback (most recent call last):
            ...
        ValueError: Lanes (Lane(name='a', size=Bytesize('48 KB')), Lane(name='b')) exceed size 48 KB
        >>> fill_lanes((Lane(name='a', size='24k'), Lane(name='b', size='25k')), u.Bytesize('48kB'))
        Traceback (most recent call last):
            ...
        ValueError: Lanes (Lane(name='a', ... exceed size 48 KB

    Empty lanes:

        >>> fill_lanes((), u.Bytesize('48kB'))
        ()
        >>> fill_lanes((), u.Bytesize('48kB'), default=True)
        (DefaultLane(size=Bytesize('48 KB')),)
    """
    if not lanes and default:
        return (DefaultLane(size=size),)
    used = 0
    missing = 0
    for lane in lanes:
        if lane.size is None:
            missing += 1
        else:
            used += lane.size
    if used > size:
        raise ValueError(f"Lanes {lanes} exceed size {size}")
    if not missing:
        return lanes
    lanesize = (size - used) // missing
    if lanesize < 1:
        raise ValueError(f"Lanes {lanes} exceed size {size}")
    return tuple(lane.new(size=lanesize) if lane.size is None else lane for lane in lanes)
