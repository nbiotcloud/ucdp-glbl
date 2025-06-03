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
Streaming Types.
"""

from typing import Any

import ucdp as u


class ValidType(u.AEnumType):
    """
    Valid Type.

    A signal of that type indicates if the related data is valid,
    driven by the transmitter.

        >>> import ucdp_glbl
        >>> valid = ucdp_glbl.stream.ValidType()
        >>> valid
        ValidType()
        >>> valid.width
        1
        >>> for item in valid.values(): print(item)
        EnumItem(0, 'invalid')
        EnumItem(1, 'valid')
    """

    keytype: u.BitType = u.BitType()

    def _build(self) -> None:
        self._add(0, "invalid")
        self._add(1, "valid")


class AcceptType(u.AEnumType):
    """
    Accept Type.

    A signal of that type indicates if the related data is taken over,
    driven by the receiver.

        >>> import ucdp_glbl
        >>> accept = ucdp_glbl.stream.AcceptType()
        >>> accept
        AcceptType()
        >>> accept.width
        1
        >>> for item in accept.values(): print(item)
        EnumItem(0, 'busy')
        EnumItem(1, 'ready')
    """

    keytype: u.BitType = u.BitType()

    def _build(self) -> None:
        self._add(0, "busy")
        self._add(1, "ready")


class AStreamType(u.AStructType):
    """
    Abstract Stream Type.

    A stream contains at least a `valid` and `accept` member.
    It is up to the child classes to define the corresponding data.
    """

    def _build(self) -> None:
        self._add("valid", ValidType(), u.FWD)
        self._add("accept", AcceptType(), u.BWD)


class StreamType(AStreamType):
    """
    Simple Stream Type with one `data` signal.

        >>> import ucdp_glbl
        >>> stream = ucdp_glbl.stream.StreamType(8)
        >>> for item in stream.values(): print(item)
        StructItem('valid', ValidType())
        StructItem('accept', AcceptType(), orientation=BWD)
        StructItem('data', UintType(8))
    """

    width: int | u.Expr

    def __init__(self, width: int | u.Expr, **kwargs: dict[str, Any]) -> None:
        super().__init__(width=width, **kwargs)

    def _build(self) -> None:
        super()._build()
        self._add("data", u.UintType(self.width))


class AnyStreamType(AStreamType):
    """
    Any Stream Type.

        >>> import ucdp_glbl
        >>> stream = ucdp_glbl.stream.AnyStreamType(u.SintType(16))
        >>> for item in stream.values(): print(item)
        StructItem('valid', ValidType())
        StructItem('accept', AcceptType(), orientation=BWD)
        StructItem('data', SintType(16))
    """

    type_: u.BaseType

    def __init__(self, type_: u.BaseType, **kwargs: dict[str, Any]) -> None:
        super().__init__(type_=type_, **kwargs)

    def _build(self) -> None:
        super()._build()
        self._add("data", self.type_)
