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

from collections.abc import Callable, Iterator
from typing import Literal

import ucdp as u
from humannum import Bytes, bytes_


class ReadOp(u.NamedLightObject):
    """
    Read Operation.

    NEXT = {data}DATA
    """

    data: Literal[None, 0, 1, "~"] = None
    """Operation On Stored Data."""
    title: str = u.Field(repr=False)
    """Title."""
    descr: str = u.Field(repr=False)
    """Description."""


_R = ReadOp(name="R", title="Read", descr="Read without Modification.")
_RC = ReadOp(name="RC", data=0, title="Read-Clear", descr="Clear on Read.")
_RS = ReadOp(name="RS", data=1, title="Read-Set", descr="Set on Read.")
# _RI = ReadOp(name="RI", data="~", title="Read-Invert", descr="Invert on Read.")


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
    title: str = u.Field(repr=False)
    """Title."""
    descr: str = u.Field(repr=False)
    """Description."""


_W = WriteOp(name="W", write="", title="Write", descr="Write Data.")
# _W0C = WriteOp(name="W0C", data="", op="&", write="", title="Write-Zero-Clear", descr="Clear On Write Zero.")
# _W0S = WriteOp(name="W0S", data="", op="|", write="~", title="Write-Zero-Set", descr="Set On Write Zero.")
_W1C = WriteOp(name="W1C", data="", op="&", write="~", title="Write-One-Clear", descr="Clear on Write One.")
_W1S = WriteOp(name="W1S", data="", op="|", write="", title="Write-One-Set", descr="Set on Write One.")


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

WO = Access(name="WO", write=_W)
W1C = Access(name="W1C", write=_W1C)
W1S = Access(name="W1S", write=_W1S)

RW = Access(name="RW", read=_R, write=_W)
RW1C = Access(name="RW1C", read=_R, write=_W1C)
RW1S = Access(name="RW1S", read=_R, write=_W1S)


ACCESSES = u.Namespace(
    (
        RO,
        RC,
        RS,
        WO,
        W1C,
        W1S,
        RW,
        RW1C,
        RW1S,
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


def forward(free: int, offset: int | None = None, align: int | None = None):
    """
    Forward Index.

    Usage:

        >>> from ucdp_glbl import addrspace
        >>> addrspace.forward(3)
        3
        >>> addrspace.forward(3, offset=4)
        4
        >>> addrspace.forward(3, align=8)
        8
        >>> addrspace.forward(8, align=8)
        8
        >>> addrspace.forward(3, offset=2)
        Traceback (most recent call last):
        ...
        ValueError: Cannot rewind to 2, already at 3
        >>> addrspace.forward(3, offset=4, align=8)
        Traceback (most recent call last):
        ...
        ValueError: 'offset' and 'align' are mutally exclusive.
    """
    if offset is None:
        if align is None:
            return free
        if free % align == 0:
            return free
        return ((free // align) + 1) * align

    if align is None:
        if offset < free:
            raise ValueError(f"Cannot rewind to {offset}, already at {free}")
        return offset

    raise ValueError("'offset' and 'align' are mutally exclusive.")


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
    bus: Access | None
    """Bus Access."""
    core: Access | None
    """Core Access."""
    upd_prio: Literal["bus", "core"] | None
    """Update Priority: None, 'b'us or 'c'core."""
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

    @property
    def bus_prio(self) -> bool:
        """Update prioriy for bus."""
        if self.upd_prio == "bus":
            return True
        if self.upd_prio == "core":
            return False
        if self.bus and (self.bus.write or (self.bus.read and self.bus.read.data is not None)):
            return True
        return False


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

    def add_field(
        self,
        name: str,
        type_: u.BaseScalarType,
        bus: Access,
        core: Access | None = None,
        upd_prio: Literal[None, "bus", "core"] | None = None,
        offset: int | u.Expr | None = None,
        is_volatile: bool | None = None,
        align: int | u.Expr | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        **kwargs,
    ) -> Field:
        """Add field."""
        if bus is not None:
            bus = cast_access(bus)
        if core is None:
            core = get_counteraccess(bus)
        else:
            core = cast_access(core)
        if self.fields:
            free = tuple(self.fields)[-1].slice.left + 1
        else:
            free = 0
        offset = forward(free, offset=offset, align=align)
        doc = u.doc_from_type(type_, title=title, descr=descr, comment=comment)
        if is_volatile is None:
            is_volatile = get_is_volatile(bus, core)
        field = self._create_field(
            name=name,
            type_=type_,
            bus=bus,
            core=core,
            upd_prio=upd_prio,
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


WordFilter = Callable[[Word], bool]
WordFields = tuple[Word, tuple[Field, ...]]


class Addrspace(u.NamedObject):
    """Address Space."""

    words: u.Namespace = u.Field(default_factory=u.Namespace, init=False, repr=False)
    """Words within Address Space."""
    width: int = 32
    """Width in Bits."""
    depth: int = 1024
    """Number of words."""

    def add_word(
        self,
        name: str,
        offset: int | u.Expr | None = None,
        align: int | u.Expr | None = None,
        depth: int | u.Expr | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        **kwargs,
    ) -> Word:
        """Add Word."""
        if self.words:
            free = tuple(self.words)[-1].slice.left + 1
        else:
            free = 0
        offset = forward(free, offset=offset, align=align)
        doc = u.Doc(title=title, descr=descr, comment=comment)
        word = self._create_word(name=name, offset=offset, width=self.width, depth=depth, doc=doc, **kwargs)
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

    @property
    def size(self) -> Bytes:
        """Size in Bytes."""
        return bytes_((self.width * self.depth) // 8)

    def get_word_hiername(self, word: Word) -> str:
        """Get Hierarchical Word Name."""
        return f"{self.name}.{word.name}"

    def get_field_hiername(self, word: Word, field: Field) -> str:
        """Get Hierarchical Field Name."""
        return f"{self.name}.{word.name}.{field.name}"

    def iter(
        self, wordfilter: WordFilter | None = None, fieldfilter: FieldFilter | None = None
    ) -> Iterator[WordFields]:
        """Iterate over words and their fields."""

        def no_wordfilter(_: Word) -> bool:
            return True

        wordfilter = wordfilter or no_wordfilter

        def no_fieldfilter(_: Word) -> bool:
            return True

        fieldfilter = fieldfilter or no_fieldfilter

        for word in self.words:
            if wordfilter(word):
                fields = [field for field in word.fields if fieldfilter(field)]
                if fields:
                    yield word, tuple(fields)


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
