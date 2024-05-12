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
Memory.
"""

import ucdp as u


class MemIoType(u.AStructType):
    """
    Memory IO-Type.

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
        >>> iotype = MemIoType.with_slicewidth(datawidth=32, addrwidth=8, writable=True, slicewidth=8)
        >>> iotype
        MemIoType(datawidth=32, addrwidth=8, writable=True, slicewidths=(8, 8, 8, 8))
        >>> for item in iotype.values(): print(item)
        StructItem('ena', EnaType(), doc=Doc(title='Memory Access Enable'))
        StructItem('addr', UintType(8), doc=Doc(title='Memory Address'))
        StructItem('wena', EnaType(), doc=Doc(title='Memory Write Enable'))
        StructItem('wdata', UintType(32), doc=Doc(title='Memory Write Data'))
        StructItem('rdata', UintType(32), orientation=BWD, doc=Doc(title='Memory Read Data'))
        StructItem('sel', UintType(4), doc=Doc(title='Slice Selects'))
    """

    datawidth: int | u.Expr
    """Data Width in Bits."""
    addrwidth: int | u.Expr
    """Address Width in Bits."""
    writable: bool
    """Read-Only or Read/Writable Memory."""
    slicewidths: tuple[int | u.Expr, ...] | None = None
    """Word Slices for Modification, Sum MUST be identical to datawidth."""
    err: bool = False
    """Report Access Error."""

    def _build(self):
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
            self._add("err", u.BitType(), title="Memory Access Failed.")

    @staticmethod
    def with_slicewidth(
        datawidth: int | u.Expr,
        addrwidth: int | u.Expr,
        writable: bool,
        slicewidth: int | u.Expr | None = None,
        err: bool = False,
    ) -> "MemIoType":
        """With Slices."""
        if slicewidth:
            if datawidth % slicewidth != 0:
                raise ValueError(f"Cannot split {datawidth} bits into slices of {slicewidth} bits")
            slices = datawidth // slicewidth
            slicewidths = (slicewidth,) * slices
        return MemIoType(datawidth=datawidth, addrwidth=addrwidth, writable=writable, slicewidths=slicewidths, err=err)
