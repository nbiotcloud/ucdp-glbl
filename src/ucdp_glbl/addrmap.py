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
Address Map.
"""

from collections.abc import Iterator

import aligntext
import ucdp as u
from icdutil import num

from .addrspace import Addrspace


class AddrMap(u.Object):
    """Address Map."""

    unique: bool = False
    fixed_size: u.Bytes | None = None

    _addrspaces: list[Addrspace] = u.PrivateField(default_factory=list)

    def add(self, addrspace: Addrspace) -> None:
        """Add Address Space."""
        self._check_size(addrspace)

        pos = self._find_pos(addrspace)

        if self.unique:
            self._check_overlapping(pos, addrspace)

        self._addrspaces.insert(pos, addrspace)

    def __iter__(self) -> Iterator[Addrspace]:
        yield from self._addrspaces

    @property
    def size(self) -> u.Bytes | None:
        """
        Size in Bytes.
        """
        size = self.fixed_size
        if size is None:
            lastaddr = self.lastaddr
            if lastaddr is None:
                return None
            size = u.Bytes(lastaddr + 1)
        return size

    @property
    def addrwidth(self) -> int | None:
        """
        Address Width.
        """
        size = self.size
        if size is None:
            return None
        return num.calc_unsigned_width(int(size - 1))

    @property
    def firstaddr(self) -> int | None:
        """
        First used address.
        """
        try:
            return self._addrspaces[0].baseaddr
        except IndexError:
            return None

    @property
    def lastaddr(self) -> int | None:
        """
        Last used address.
        """
        try:
            return self._addrspaces[-1].endaddr
        except IndexError:
            return None

    @property
    def addrslice(self) -> u.Slice | None:
        """
        Address Slice.
        """
        addrspaces = self._addrspaces
        addrwidth = self.addrwidth
        if addrwidth is None or not addrspaces:
            return None

        minsize = int(min(addrspace.size for addrspace in addrspaces))

        # Ensure at least one address decoding bit
        if minsize == self.size:
            left = addrwidth
        else:
            left = addrwidth - 1

        right = min(num.calc_lowest_bit_set(minsize), left)
        return u.Slice(left=left, right=right)

    def get_free_baseaddr(self, size: u.Bytes, align=None, start=None) -> int:
        """
        Return baseaddress of free window with `size`.

        Args:
            size: Window Size

        Keyword Args:
            align: Alignment, default aligned to size
            start: Start search behind given address
        """
        size = u.Bytes(size)
        if align is None:
            align = size
        if start is None:
            lastaddr = self.lastaddr
            start = lastaddr + 1 if lastaddr else 0

        baseaddr = u.Hex(self._find_space(size, align, start))

        # End Check
        endaddr = baseaddr + size
        size = self.fixed_size
        if size is not None:
            if endaddr >= size:
                size_hex = u.Hex(size)
                raise ValueError(f"End address {endaddr} would exceed maximum size {size_hex} ({size})")

        return baseaddr

    def _find_space(self, size, align, start):
        addr = start = num.align(start, align=align)
        for item in self._addrspaces:
            if item.endaddr < start:
                # skip all before start
                addr = max(num.align(item.nextaddr, align=align), addr)
                continue
            if item.baseaddr >= (addr + size):
                break
            addr = num.align(item.nextaddr, align=align)
        return addr

    def get_overview(self, skip_addrspaces: bool = False, skip_words_fields: bool = False) -> str:
        """
        Return overview table.
        """
        parts = ["", f"Size: {self.size}"]
        if not skip_addrspaces:
            parts.append(self._get_addrspaces_overview())
        if not skip_words_fields:
            parts.append(self._get_word_fields_overview())
        return "\n\n".join(parts)

    def _get_addrspaces_overview(self) -> str:
        data = [
            ("Namespace", "Type", "Base", "Size", "Attributes"),
            ("---------", "----", "----", "----", "----------"),
        ]
        for addrspace in self:
            classname = addrspace.__class__.__name__.replace("Addrspace", "") or "-"
            attrs = []
            if addrspace.is_sub:
                attrs.append("Sub")
            if addrspace.is_volatile:
                attrs.append("Volatile")
            data.append(
                (
                    addrspace.name,
                    classname,
                    addrspace.base,
                    addrspace.org,
                    ",".join(attrs),
                )
            )
        return aligntext.align(data, seps=(" | ",), sepfirst="| ", seplast=" |") + "\n"

    def _get_word_fields_overview(self) -> str:
        data = [
            ("Addrspace", "Word", "Field", "Offset", "Access", "Reset", "Attributes"),
            ("---------", "----", "-----", "------", "------", "-----", "----------"),
        ]
        resolver = u.ExprResolver()
        for addrspace in self:
            attrs = []
            if addrspace.is_volatile:
                attrs.append("Volatile")
            data.append(
                (
                    addrspace.name,
                    "",
                    "",
                    addrspace.base,
                    addrspace.access,
                    "",
                    ",".join(attrs),
                )
            )
            for word in addrspace.words:
                attrs = []
                if word.is_volatile:
                    attrs.append("Volatile")
                data.append(
                    (
                        addrspace.name,
                        word.name,
                        "",
                        f"  +{word.slice}",
                        word.access,
                        "",
                        ",".join(attrs),
                    )
                )
                for field in word.fields:
                    attrs = []
                    if field.is_volatile:
                        attrs.append("Volatile")
                    if field.is_const:
                        attrs.append("CONST")
                    data.append(
                        (
                            addrspace.name,
                            word.name,
                            field.name,
                            f"    {field.slice}",
                            str(field.access),
                            resolver.resolve_value(field.type_),
                            ",".join(attrs),
                        )
                    )

        return aligntext.align(data, seps=(" | ",), sepfirst="| ", seplast=" |") + "\n"

    def _check_size(self, addrspace: Addrspace) -> None:
        fixed_size = self.fixed_size
        if fixed_size is not None:
            if addrspace.endaddr >= fixed_size:
                raise ValueError(f"{addrspace!r}: exceeds maximum size: {fixed_size}.")

    def _find_pos(self, addrspace: Addrspace) -> int:
        baseaddr = addrspace.baseaddr
        for pos, item in enumerate(self._addrspaces):
            if item.baseaddr > baseaddr:
                return pos
        return len(self._addrspaces)

    def _check_overlapping(self, pos: int, addrspace: Addrspace) -> None:
        addrspaces = self._addrspaces
        # lower
        try:
            lower = addrspaces[pos - 1]
        except IndexError:
            pass
        else:
            if addrspace.is_overlapping(lower):
                raise ValueError(f"{addrspace!r} overlaps with {lower!r}")
        # upper
        try:
            upper = addrspaces[pos]
        except IndexError:
            pass
        else:
            if addrspace.is_overlapping(upper):
                raise ValueError(f"{addrspace!r} overlaps with {upper!r}")
