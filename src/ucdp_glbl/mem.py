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
Memory Types.
"""

from typing import Literal, TypeAlias

import ucdp as u

SliceWidths: TypeAlias = tuple[int | u.Expr, ...]
"""Word Slice Widths."""

Addressing: TypeAlias = Literal["byte", "data"]
"""Address Mode."""


class MemIoType(u.AStructType):
    """
    Memory IO-Type.

    Attributes:
        datawidth: Data Width in Bits
        addrwidth: Address Width in Bits
        writable: Read-Only or Read/Writable Memory
        slicewidths: Word Slices for Modification, Sum MUST be identical to datawidth
        err: Report Access Error
        addressing: Addressing Mode

    ROM Example:

        >>> from ucdp_glbl.mem import MemIoType
        >>> iotype = MemIoType(datawidth=32, addrwidth=8, writable=False)
        >>> iotype
        MemIoType(datawidth=32, addrwidth=8, writable=False)
        >>> for item in iotype.values(): print(item)
        StructItem('ena', EnaType(), doc=Doc(title='Memory Access Enable'))
        StructItem('addr', UintType(8), doc=Doc(title='Memory Address'))
        StructItem('rdata', UintType(32), orientation=BWD, doc=Doc(title='Memory Read Data'))

    RAM Example:

        >>> from ucdp_glbl.mem import MemIoType
        >>> iotype = MemIoType(datawidth=32, addrwidth=8, writable=True)
        >>> iotype
        MemIoType(datawidth=32, addrwidth=8, writable=True)
        >>> for item in iotype.values(): print(item)
        StructItem('ena', EnaType(), doc=Doc(title='Memory Access Enable'))
        StructItem('addr', UintType(8), doc=Doc(title='Memory Address'))
        StructItem('wena', EnaType(), doc=Doc(title='Memory Write Enable'))
        StructItem('wdata', UintType(32), doc=Doc(title='Memory Write Data'))
        StructItem('rdata', UintType(32), orientation=BWD, doc=Doc(title='Memory Read Data'))

    RAM Example with Byte Access and error:

        >>> from ucdp_glbl.mem import MemIoType
        >>> iotype = MemIoType.with_slicewidth(datawidth=32, addrwidth=8, writable=True, slicewidth=8, err=True)
        >>> iotype
        MemIoType(datawidth=32, addrwidth=8, writable=True, slicewidths=(8, 8, 8, 8), err=True)
        >>> for item in iotype.values(): print(item)
        StructItem('ena', EnaType(), doc=Doc(title='Memory Access Enable'))
        StructItem('addr', UintType(8), doc=Doc(title='Memory Address'))
        StructItem('wena', EnaType(), doc=Doc(title='Memory Write Enable'))
        StructItem('wdata', UintType(32), doc=Doc(title='Memory Write Data'))
        StructItem('rdata', UintType(32), orientation=BWD, doc=Doc(title='Memory Read Data'))
        StructItem('sel', UintType(4), doc=Doc(title='Slice Selects'))
        StructItem('err', BitType(), orientation=BWD, doc=Doc(title='Memory Access Failed.'))

    Non-Slicable:

        >>> MemIoType.with_slicewidth(datawidth=31, addrwidth=8, writable=True, slicewidth=8)
        Traceback (most recent call last):
        ...
        ValueError: Cannot split 31 bits into slices of 8 bits

    """

    datawidth: int | u.Expr
    addrwidth: int | u.Expr
    writable: bool
    slicewidths: SliceWidths | None = None
    err: bool = False
    addressing: Addressing = "byte"

    def _build(self) -> None:
        datatype = u.UintType(self.datawidth)
        addrtype = u.UintType(self.addrwidth)
        self._add("ena", u.EnaType(), title="Memory Access Enable")
        self._add("addr", addrtype, title="Memory Address")
        if self.writable:
            self._add("wena", u.EnaType(), title="Memory Write Enable")
            self._add("wdata", datatype, title="Memory Write Data")
        self._add("rdata", datatype, title="Memory Read Data", orientation=u.BWD)
        if self.slicewidths:
            self._add("sel", u.UintType(len(self.slicewidths)), title="Slice Selects")
        if self.err:
            self._add("err", u.BitType(), title="Memory Access Failed.", orientation=u.BWD)

    @staticmethod
    def with_slicewidth(
        datawidth: int | u.Expr,
        addrwidth: int | u.Expr,
        writable: bool,
        slicewidth: int | u.Expr | None = None,
        err: bool = False,
    ) -> "MemIoType":
        """Create `MemIoType` based on given `slicewidth` instead of individual `slicewidths`."""
        slicewidths = calc_slicewidths(datawidth, slicewidth)
        return MemIoType(datawidth=datawidth, addrwidth=addrwidth, writable=writable, slicewidths=slicewidths, err=err)


def calc_slicewidths(datawidth: int | u.Expr, slicewidth: int | u.Expr | None = None) -> SliceWidths | None:
    """
    Calculate slicewidths.

        >>> calc_slicewidths(32) is None
        True
        >>> calc_slicewidths(32, slicewidth=8)
        (8, 8, 8, 8)
        >>> calc_slicewidths(32, slicewidth=5)
        Traceback (most recent call last):
          ...
        ValueError: Cannot split 32 bits into slices of 5 bits
    """
    if slicewidth is None:
        return None
    if datawidth % slicewidth != 0:
        raise ValueError(f"Cannot split {datawidth} bits into slices of {slicewidth} bits")
    slices = datawidth // slicewidth
    return (slicewidth,) * slices
