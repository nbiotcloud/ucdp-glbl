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
Generic Addressed Slave.
"""

import ucdp as u
from icdutil import num

from .addrdecoder import AddrDecoder
from .addrspace import Addrspace


class AddrSlave(u.NamedObject):
    """
    Slave.
    """

    addrdecoder: AddrDecoder = u.Field(repr=False)
    """Demultiplexer Addressing This Slave."""

    ref: u.Object | str | None = None
    """Addressed Module."""

    def add_addrrange(self, subbaseaddr=u.AUTO, size: u.Bytes | None = None) -> "SlaveAddrspace":
        """
        Add Address Range.

        Keyword Args:
            subbaseaddr: Sub Start Address. Take next free if 'AUTO'.
            size: Address Range Size (i.e. '4k')
            ref: Referenced Object or instance path to it.
        """
        addrdecoder = self.addrdecoder
        addrmap = addrdecoder.addrmap

        # size
        if size is None:
            size = addrdecoder.default_size
        else:
            size = u.Bytes(size)

        # subbaseaddr
        if size is not None:
            align = num.calc_next_power_of(size)
            if subbaseaddr is u.AUTO:
                subbaseaddr = addrmap.get_free_baseaddr(align)
            if subbaseaddr != num.align(subbaseaddr, align=align):
                raise ValueError(f"subbaseaddr {subbaseaddr!r} is not aligned to size {align!r}")

        addrspace = SlaveAddrspace(
            name=self.name,
            baseaddr=subbaseaddr,
            size=size,
            slave=self,
            is_sub=addrdecoder.is_sub,
        )
        addrmap.add(addrspace)
        return addrspace


class SlaveAddrspace(Addrspace):
    """Slave Address Space."""

    slave: AddrSlave
