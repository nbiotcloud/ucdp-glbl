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
Address Space.
"""

from collections import defaultdict
from collections.abc import Callable, Iterator
from typing import Literal, Optional

import ucdp as u
from humannum import bytes_
from icdutil import num


class ReadOp(u.NamedLightObject):
    """
    Read Operation.

    NEXT = {data}DATA
    """

    data: Literal[None, 0, 1, "~"] = None
    """Operation On Stored Data."""
    once: bool = False
    """Operation is just allowed once."""
    title: str = u.Field(repr=False)
    """Title."""
    descr: str = u.Field(repr=False)
    """Description."""


_R = ReadOp(name="R", title="Read", descr="Read without Modification.")
_RC = ReadOp(name="RC", data=0, title="Read-Clear", descr="Clear on Read.")
_RS = ReadOp(name="RS", data=1, title="Read-Set", descr="Set on Read.")
_RT = ReadOp(name="RT", data="~", title="Read-Toggle", descr="Toggle on Read.")
_RP = ReadOp(name="RP", once=True, title="Read-Protected", descr="Data is hidden after first Read.")


class WriteOp(u.NamedLightObject):
    """
    Write Operation.

    NEXT = {data}DATA {op} {write}WRITE
    """

    data: Literal[None, "", "~"] = None
    """Operation On Stored Data."""
    op: Literal[None, 0, 1, "&", "|"] = None
    """Operation On Stored and Incoming Data."""
    write: Literal[None, "", "~"] = None
    """Operation On Incoming Data."""
    once: bool = False
    """Operation is just allowed once."""
    title: str = u.Field(repr=False)
    """Title."""
    descr: str = u.Field(repr=False)
    """Description."""


_W = WriteOp(name="W", write="", title="Write", descr="Write Data.")
_W0C = WriteOp(name="W0C", data="", op="&", write="", title="Write-Zero-Clear", descr="Clear On Write Zero.")
_W0S = WriteOp(name="W0S", data="", op="|", write="~", title="Write-Zero-Set", descr="Set On Write Zero.")
_W1C = WriteOp(name="W1C", data="", op="&", write="~", title="Write-One-Clear", descr="Clear on Write One.")
_W1S = WriteOp(name="W1S", data="", op="|", write="", title="Write-One-Set", descr="Set on Write One.")
_WL = WriteOp(name="WL", write="", once=True, title="Write Locked", descr="Write Data once and Lock.")


class Access(u.NamedLightObject):
    """Access."""

    read: ReadOp | None = None
    write: WriteOp | None = None

    @property
    def title(self):
        """Title."""
        readtitle = self.read and self.read.title
        writetitle = self.write and self.write.title
        if readtitle and writetitle:
            return f"{readtitle}/{writetitle}"
        return readtitle or writetitle

    @property
    def descr(self):
        """Description."""
        readdescr = self.read and self.read.descr
        writedescr = self.write and self.write.descr
        if readdescr and writedescr:
            return f"{readdescr} {writedescr}"
        return readdescr or writedescr

    def __str__(self):
        return self.name


RO = Access(name="RO", read=_R)
RC = Access(name="RC", read=_RC)
RS = Access(name="RS", read=_RS)
RT = Access(name="RT", read=_RT)
RP = Access(name="RP", read=_RP)

WO = Access(name="WO", write=_W)
W0C = Access(name="W0C", write=_W0C)
W0S = Access(name="W0S", write=_W0S)
W1C = Access(name="W1C", write=_W1C)
W1S = Access(name="W1S", write=_W1S)
WL = Access(name="WL", write=_WL)

RW = Access(name="RW", read=_R, write=_W)
RW0C = Access(name="RW0C", read=_R, write=_W0C)
RW0S = Access(name="RW0S", read=_R, write=_W0S)
RW1C = Access(name="RW1C", read=_R, write=_W1C)
RW1S = Access(name="RW1S", read=_R, write=_W1S)
RWL = Access(name="RWL", read=_R, write=_WL)


ACCESSES = u.Namespace(
    (
        RO,
        RC,
        RS,
        RT,
        RP,
        WO,
        W0C,
        W0S,
        W1C,
        W1S,
        WL,
        RW,
        RW0C,
        RW0S,
        RW1C,
        RW1S,
        RWL,
    )
)
ACCESSES.lock()

_COUNTERACCESS = {
    None: RO,
    RO: RW,
    # RC: ,
    # RS: ,
    # RI: ,
    WO: RO,
    # W1C: ,
    # W1S: ,
    RW: RO,
    # RW1C: ,
    # RW1S: ,
    # RCW: ,
    # RCW1C: ,
    # RCW1S: ,
    # RSW: ,
    # RSW1C: ,
    # RSW1S: ,
    # RIW: ,
    # RIW1C: ,
    # RIW1S: ,
}


def cast_access(value: str | Access) -> Access:
    """
    Cast Access.

    Usage:

        >>> from ucdp_glbl import addrspace
        >>> access = addrspace.cast_access("RO")
        >>> access
        Access(name='RO', read=ReadOp(name='R'))
        >>> cast_access(access)
        Access(name='RO', read=ReadOp(name='R'))
    """
    if isinstance(value, Access):
        return value
    return ACCESSES[value]


def get_counteraccess(access: Access) -> Access | None:
    """
    Get Counter Access.

    Usage:

        >>> from ucdp_glbl import addrspace
        >>> str(addrspace.get_counteraccess(addrspace.RO))
        'RW'
        >>> str(addrspace.get_counteraccess(addrspace.RW))
        'RO'
    """
    return _COUNTERACCESS.get(access, None)


class Field(u.NamedLightObject):
    """Field."""

    type_: u.BaseScalarType
    """Type."""
    bus: Access | None = None
    """Bus Access."""
    core: Access | None = None
    """Core Access."""
    offset: int | u.Expr
    """Rightmost Bit Position."""
    is_volatile: bool = False
    """Volatile."""
    doc: u.Doc = u.Doc()
    """Documentation."""

    @property
    def slice(self) -> u.Slice:
        """Slice with Word."""
        return u.Slice(width=self.type_.width, right=self.offset)

    @property
    def is_const(self) -> bool:
        """Field is Constant."""
        return get_is_const(self.bus, self.core)

    @property
    def access(self) -> str:
        """Access."""
        bus = (self.bus and self.bus.name) or "-"
        core = (self.core and self.core.name) or "-"
        return f"{bus}/{core}"


FieldFilter = Callable[[Field], bool]


class Word(u.NamedObject):
    """Word."""

    fields: u.Namespace = u.Field(default_factory=u.Namespace, init=False, repr=False)
    """Fields within Word."""
    offset: int | u.Expr
    """Rightmost Word Position."""
    width: int
    """Width in Bits."""
    depth: int | u.Expr | None = None
    """Number of words."""
    doc: u.Doc = u.Doc()
    """Documentation"""

    bus: Access | None = None
    core: Access | None = None
    is_volatile: bool | None = None

    def add_field(
        self,
        name: str,
        type_: u.BaseScalarType,
        bus: Access | None = None,
        core: Access | None = None,
        offset: int | u.Expr | None = None,
        align: int | u.Expr | None = None,
        is_volatile: bool | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        **kwargs,
    ) -> Field:
        """Add field."""
        if bus is not None:
            bus = cast_access(bus)
        else:
            bus = self.bus
        if core is not None:
            core = cast_access(core)
        else:
            core = self.core
        if self.fields:
            free = tuple(self.fields)[-1].slice.left + 1
        else:
            free = 0
        offset = num.align(free, offset=offset, align=align)
        doc = u.doc_from_type(type_, title=title, descr=descr, comment=comment)
        if is_volatile is None:
            is_volatile = self.is_volatile
        if is_volatile is None:
            is_volatile = get_is_volatile(bus, core)
        field = self._create_field(
            name=name,
            type_=type_,
            bus=bus,
            core=core,
            offset=offset,
            is_volatile=is_volatile,
            doc=doc,
            **kwargs,
        )
        if field.slice.left >= self.width:
            raise ValueError(f"Field {field.name!r} exceeds word width of {self.width}")
        self.fields.add(field)
        return field

    def _create_field(self, **kwargs) -> Field:
        return Field(**kwargs)

    @property
    def slice(self) -> u.Slice:
        """Slice with Address Space."""
        if self.depth is None:
            return u.Slice(left=self.offset, right=self.offset)
        return u.Slice(width=self.depth, right=self.offset)

    def lock(self):
        """Lock For Modification."""
        self.fields.lock()

    @property
    def wordsize(self) -> float:
        """Word Size in Bytes."""
        return self.width * (self.depth or 1) / 8

    @property
    def byteoffset(self) -> u.Hex:
        """Offset in Bytes, if word width is multiple of 8."""
        if (self.width % 8) != 0:
            raise ValueError(f"'byteoffset' is only available on words with 'width' multiple of 8 (not {self.width})")
        return self.offset * self.width // 8

    @property
    def access(self) -> str:
        """Access."""
        if self.bus or self.core:
            bus = (self.bus and self.bus.name) or "-"
            core = (self.core and self.core.name) or "-"
            return f"{bus}/{core}"
        return ""


def _bytealign(width, free, offset=None, align=None, byteoffset=None, bytealign=None):
    if byteoffset is None and bytealign is None:
        pass
    elif (width % 8) == 0:
        bytesperword = width // 8
        if byteoffset is not None:
            if offset is not None:
                raise ValueError("'byteoffset' and 'offset' are mutally exclusive")
            offset = byteoffset // bytesperword
        if bytealign is not None:
            if align is not None:
                raise ValueError("'bytealign' and 'align' are mutally exclusive")
            align = bytealign // bytesperword
    else:
        raise ValueError(f"'byteoffset/bytealign' are only available on 'width' multiple of 8 (not {width})")
    return num.align(free, offset=offset, align=align)


WordFilter = Callable[[Word], bool]
WordFields = tuple[Word, tuple[Field, ...]]

FillWordFactory = Callable[["Addrspace", int, int, int], Word]
FillFieldFactory = Callable[[Word, int, int, int], Field]


class Addrspace(u.NamedObject):
    """Address Space."""

    baseaddr: u.Hex = 0
    """Base Address"""
    width: int = 32
    """Width in Bits."""
    depth: int = u.Field(repr=False)
    """Number of words."""
    size: u.Bytes
    """Size in Bytes."""
    is_sub: bool = True
    """Address Decoder Just Compares `addrwidth` LSBs."""
    words: u.Namespace = u.Field(default_factory=u.Namespace, repr=False)
    """Words within Address Space."""

    bus: Access | None = None
    core: Access | None = None
    is_volatile: bool | None = None

    def __init__(
        self,
        width: int = 32,
        depth: int | None = None,
        size: u.Bytes | None = None,
        bus: Access | str | None = None,
        core: Access | str | None = None,
        **kwargs,
    ):
        # Provide either 'size' or 'depth' and calculate the other
        if size is None:
            if depth is None:
                raise ValueError("Either 'depth' or 'size' are required.")
            size = bytes_((width * depth) // 8)
        else:
            depth_calculated = int(bytes_(size) * 8 // width)
            if depth is not None and depth != depth_calculated:
                raise ValueError("'depth' and 'size' are mutally exclusive.")
            depth = depth_calculated
        if bus is not None:
            bus = cast_access(bus)
        if core is not None:
            core = cast_access(core)
        super().__init__(width=width, depth=depth, size=size, bus=bus, core=core, **kwargs)

    @property
    def addrwidth(self) -> int:
        """Address Width."""
        return num.calc_unsigned_width(int(self.size) - 1)

    @property
    def endaddr(self) -> u.Hex:
        """End Address - `baseaddr+size-1`."""
        return self.baseaddr + self.size - 1

    @property
    def nextaddr(self) -> u.Hex:
        """Next Free Address - `baseaddr+size`."""
        return self.baseaddr + self.size

    @property
    def wordsize(self) -> float:
        """Number of Bytes Per Word."""
        return self.width / 8

    @property
    def size_used(self) -> u.Bytes:
        """Number of Bytes Used."""
        return bytes_(int(sum(word.wordsize for word in self.words)))

    @property
    def free_offset(self) -> int:
        """Free Offset."""
        if self.words:
            return tuple(self.words)[-1].slice.left + 1
        return 0

    @property
    def org(self) -> str:
        """Organization."""
        return f"{self.depth}x{self.width} ({self.size})"

    @property
    def base(self) -> str:
        """Base."""
        if self.is_sub:
            return f"+{self.baseaddr}"
        return f"{self.baseaddr}"

    @property
    def access(self) -> str:
        """Access."""
        if self.bus or self.core:
            bus = (self.bus and self.bus.name) or "-"
            core = (self.core and self.core.name) or "-"
            return f"{bus}/{core}"
        return ""

    def add_word(
        self,
        name: str,
        offset: int | u.Expr | None = None,
        align: int | u.Expr | None = None,
        byteoffset: int | u.Expr | None = None,
        bytealign: int | u.Expr | None = None,
        depth: int | u.Expr | None = None,
        bus: Access | None = None,
        core: Access | None = None,
        is_volatile: bool | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        **kwargs,
    ) -> Word:
        """Add Word."""
        free = self.free_offset
        offset = _bytealign(self.width, free, offset=offset, align=align, byteoffset=byteoffset, bytealign=bytealign)
        doc = u.Doc(title=title, descr=descr, comment=comment)
        if bus is None:
            bus = self.bus
        if core is None:
            core = self.core
        if is_volatile is None:
            is_volatile = self.is_volatile
        word = self._create_word(
            name=name,
            offset=offset,
            width=self.width,
            depth=depth,
            doc=doc,
            bus=bus,
            core=core,
            is_volatile=is_volatile,
            **kwargs,
        )
        if word.slice.left >= self.depth:
            raise ValueError(f"Word {word.name!r} exceeds address space depth of {self.depth}")
        self.words.add(word)
        return word

    def _create_word(self, **kwargs) -> Word:
        return Word(**kwargs)

    def lock(self):
        """Lock For Modification."""
        for word in self.words:
            word.lock()
        self.words.lock()

    def get_word_hiername(self, word: Word) -> str:
        """Get Hierarchical Word Name."""
        return f"{self.name}.{word.name}"

    def get_field_hiername(self, word: Word, field: Field) -> str:
        """Get Hierarchical Field Name."""
        return f"{self.name}.{word.name}.{field.name}"

    def iter(  # noqa: C901
        self,
        wordfilter: WordFilter | None = None,
        fieldfilter: FieldFilter | None = None,
        fill_word: FillWordFactory | None = None,
        fill_field: FillFieldFactory | None = None,
        fill_word_end: bool = False,
        fill_field_end: bool = False,
    ) -> Iterator[WordFields]:
        """Iterate over words and their fields."""

        def no_wordfilter(_: Word) -> bool:
            return True

        wordfilter = wordfilter or no_wordfilter

        def no_fieldfilter(_: Word) -> bool:
            return True

        fieldfilter = fieldfilter or no_fieldfilter

        def create_word(counter, offset, size) -> WordFields:
            idx = counter[None]
            fword = fill_word(self, idx, offset, size)
            counter[None] = idx + 1
            if fill_field and fill_field_end:
                return fword, (fill_field(fword, 0, 0, word.width),)
            return fword, ()

        def fill_fields(word, fields) -> Iterator:
            offset = 0
            idx = 0
            for field in fields:
                if not fieldfilter(field):
                    continue

                # fill before
                if field.offset > offset:
                    yield fill_field(word, idx, offset, field.offset - offset)
                    idx += 1

                yield field

                offset = field.slice.nxt

            if fill_field_end:
                if word.width > offset:
                    yield fill_field(word, idx, offset, word.width - offset)

        counter: dict[None, int] = defaultdict(int)
        offset = 0
        for word in self.words:
            if not wordfilter(word):
                continue

            # fill before
            if fill_word and word.offset > offset:
                yield create_word(counter, offset, word.offset - offset)
                offset = word.offset + (word.depth or 1)

            if fill_field:
                fields = tuple(fill_fields(word, word.fields))
            else:
                fields = tuple(field for field in word.fields if fieldfilter(field))

            if fields:
                yield word, fields

        if fill_word and fill_word_end:
            yield create_word(counter, offset, self.depth)

    def is_overlapping(self, other: "Addrspace") -> bool:
        """
        Determine both Address Spaces Overlap.

        >>> one = Addrspace(name='one', baseaddr=0x2000, size='4kB')
        >>> two = Addrspace(name='two', baseaddr=0x3000, size='4kB')
        >>> three = Addrspace(name='three', baseaddr=0x2000, size='5kB')
        >>> one.is_overlapping(two)
        False
        >>> one.is_overlapping(three)
        True
        >>> three.is_overlapping(one)
        True
        >>> three.is_overlapping(two)
        True
        """
        if self.baseaddr < other.baseaddr:
            return self.endaddr >= other.baseaddr
        return self.baseaddr <= other.endaddr

    def get_intersect(self, other: "Addrspace") -> Optional["Addrspace"]:
        """
        Get Intersection.

        >>> one = Addrspace(name='one', baseaddr=0x2000, size='4kB')
        >>> two = Addrspace(name='two', baseaddr=0x3000, size='4kB')
        >>> three = Addrspace(name='three', baseaddr=0x2000, size='5kB')
        >>> one.get_intersect(two)
        >>> one.get_intersect(three)
        Addrspace(name='one', baseaddr=Hex('0x2000'), size=Bytes('4 KB'))
        >>> three.get_intersect(one)
        Addrspace(name='three', baseaddr=Hex('0x2000'), size=Bytes('4 KB'))
        >>> three.get_intersect(two)
        Addrspace(name='three', baseaddr=Hex('0x3000'), size=Bytes('1 KB'))
        """
        baseaddr = max(self.baseaddr, other.baseaddr)
        endaddr = min(self.endaddr, other.endaddr)
        size = endaddr - baseaddr + 1
        if size <= 0:
            return None
        words = u.Namespace()
        # TODO: add words
        return self.new(baseaddr=baseaddr, size=size, depth=None, words=words)

    def join(self, other: "Addrspace") -> Optional["Addrspace"]:
        """
        Join if Possible.

        TODO: doc
        """
        if other.is_sub:
            return self._join(self, other)
        if self.is_sub:
            return self._join(other, self)
        return other.get_intersect(self)

    @staticmethod
    def _join(one: "Addrspace", sub: "Addrspace") -> Optional["Addrspace"]:
        baseaddr = one.baseaddr + sub.baseaddr
        endaddr = one.baseaddr + sub.endaddr
        if endaddr > one.endaddr:
            raise ValueError(f"{sub!r} does not fit into {one!r}")
        return sub.new(baseaddr=baseaddr, size=min(one.size, sub.size), is_sub=one.is_sub, words=sub.words)


def get_is_volatile(bus: Access | None, core: Access | None) -> bool:
    """Calc Volatile Flag based on Accesses."""
    if bus is not None:
        if bus.read and bus.read.data is not None:
            # Read operation on bus manipulates data
            return True
        if core is None:
            # Bus Access Only
            return False
    if core is not None:
        if core.read and core.read.data is not None:
            # Read operation on core side manipulates data
            return True
        if bus is not None and bus.write and core.write:
            # Two-Sides can manipulate
            return True
    return False


def get_is_const(bus: Access | None, core: Access | None) -> bool:
    """Calc Is Constant Flag based on Accesses."""
    if bus is not None:
        if bus.write:
            return False
        if bus.read and bus.read.data is not None:
            return False
    if core is not None:
        if core.read and core.read.data is not None:
            return False
        if core.write:
            return False
    return True


def create_fill_word(idx, offset, depth) -> Word:
    """Create Fill Word."""
    return Word(name=f"reserved{idx}", offset=offset, depth=depth)


def create_fill_field(idx, offset, depth) -> Field:
    """Create Fill Field."""
    return Field(name=f"reserved{idx}", offset=offset, depth=depth)
