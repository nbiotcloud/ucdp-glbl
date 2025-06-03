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
Find Module With Specific Attribute Or Method.

    >>> import ucdp as u
    >>> class SubMod(u.AMod):
    ...     def _build(self):
    ...         pass
    >>> class AnotherSubMod(u.AMod):
    ...     def _build(self):
    ...         pass
    ...     @property
    ...     def feature(self):
    ...         return "Hello World"
    >>> class TopMod(u.AMod):
    ...     def _build(self):
    ...         SubMod(self, 'u_sub')
    ...         AnotherSubMod(self, 'u_anothersub')

    >>> from ucdp_glbl.finder import find
    >>> top = TopMod()
    >>> find([top], 'feature')
    (<ucdp_glbl.finder.AnotherSubMod(inst='top/u_anothersub', ...)>, 'Hello World')
"""

from collections.abc import Iterable
from typing import Any

import ucdp as u


def find(mods: Iterable[u.BaseMod], name: str) -> tuple[u.BaseMod, Any]:
    """Find module with attribute named `name`, starting from top to bottom."""
    undefined = object()
    attrs: list[Any] = []
    attrmods: list[u.BaseMod] = []
    insts = list(mods)
    while insts and not attrs:
        subinsts = []
        # Search for 'name' on all modules.
        for inst in insts:
            subinsts.extend(inst.insts)
            attr = getattr(inst, name, undefined)
            if attr is not undefined:
                attrs.append(attr)
                attrmods.append(inst)
        # None of the modules had a 'name' property. So continue on next level
        if attrs:
            break
        insts = subinsts

    if not attrs:
        raise ValueError(f"No module found which implements {name!r}")

    if len(attrs) == 1:
        return attrmods[0], attrs[0]

    lines = [f"Multiple modules implement {name!r}:"]
    lines += [f"  {mod!r}" for mod in attrmods]
    lines.append(f"Implement {name!r} on a parent module or choose a different top.")
    raise ValueError("\n".join(lines))
