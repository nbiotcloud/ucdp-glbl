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
Address Spaces.
"""

from collections.abc import Callable

import ucdp as u

from .addrmap import AddrMap
from .addrspaces import Addrspaces

Defines = dict[str, str]

GetAttrspacesFunc = Callable[[], Addrspaces]


def get_addrmap(mod: u.BaseMod, defines: Defines | None = None) -> AddrMap:
    """Search Address Spaces and Create Address Map."""
    addrmap = AddrMap()
    for addrspace in get_addrspaces(mod):
        addrmap.add(addrspace)
    return addrmap


def get_addrspaces(mod: u.BaseMod, defines: Defines | None = None) -> Addrspaces:
    """Search Address Spaces."""
    func = _find_get_addrspaces([mod])
    defines = defines or {}
    return func(**defines)


def _find_get_addrspaces(mods: list[u.BaseMod]) -> GetAttrspacesFunc:
    funcs: list[GetAttrspacesFunc] = []
    funcmods: list[u.BaseMod] = []
    while mods and not funcs:
        subinsts = []
        # Search for 'get_addrspaces' on all modules.
        for mod in mods:
            subinsts.extend(mod.insts)
            func = getattr(mod, "get_addrspaces", None)
            if func:
                funcs.append(func)
                funcmods.append(mod)
        # None of the modules had a 'get_addrspaces' function. So continue on next level
        if funcs:
            break
        mods = subinsts

    if not funcs:
        raise ValueError("No module found which implements 'get_addrspaces'")

    if len(funcs) == 1:
        return funcs[0]

    lines = ["Multiple modules implement 'get_addrspaces':"]
    lines += [f"  {mod!r}" for mod in funcmods]
    lines.append("Implement 'get_addrspaces' on a parent module or choose a different top.")
    raise ValueError("\n".join(lines))
