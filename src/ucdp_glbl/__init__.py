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
"""Unified Chip Design Platform - Global."""

from .addrdecoder import AddrDecoder
from .addrmap import AddrMap, create_fill_addrspace
from .addrmapfinder import Defines, GetAttrspacesFunc, get_addrmap, get_addrspaces
from .addrmaster import AddrMaster
from .addrmatrix import AddrMatrix
from .addrref import AddrRef
from .addrslave import AddrSlave
from .addrspace import (
    ACCESSES,
    Access,
    Addrspace,
    Field,
    ReadOp,
    ReservedAddrspace,
    Word,
    WriteOp,
    create_fill_field,
    create_fill_word,
)
from .addrspacealias import AddrspaceAlias
from .addrspaces import Addrspaces, join_addrspaces
from .const import NOREF

__all__ = [
    "Access",
    "ACCESSES",
    "AddrDecoder",
    "AddrMap",
    "AddrMaster",
    "ReservedAddrspace",
    "AddrMatrix",
    "AddrRef",
    "AddrSlave",
    "Addrspace",
    "AddrspaceAlias",
    "Addrspaces",
    "create_fill_addrspace",
    "create_fill_field",
    "create_fill_word",
    "Defines",
    "Field",
    "get_addrmap",
    "get_addrspaces",
    "GetAttrspacesFunc",
    "join_addrspaces",
    "NOREF",
    "ReadOp",
    "Word",
    "WriteOp",
]
