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
Demux.
"""

from logging import getLogger

import ucdp as u

from .addrmap import AddrMap
from .addrmapfinder import get_addrspaces
from .addrspaces import Addrspaces, join_addrspaces
from .const import NOREF

LOGGER = getLogger(__name__)


class AddrDecoder(u.Object):
    """
    Demultiplexer.
    """

    addrmap: AddrMap = u.Field(default_factory=lambda: AddrMap(unique=True))
    """Address Map for All Slaves."""

    slaves: u.Namespace = u.Field(default_factory=u.Namespace)
    """Slaves."""

    default_size: u.Bytes | None = None
    """Default Size if not given."""

    is_sub: bool = False

    def get_addrspaces(self, **kwargs) -> Addrspaces:
        """Address Spaces."""
        for addrspace in self.addrmap:
            ref = addrspace.slave.ref
            if ref is None or ref is NOREF:
                continue
            yield from join_addrspaces(addrspace, get_addrspaces(ref, kwargs))
