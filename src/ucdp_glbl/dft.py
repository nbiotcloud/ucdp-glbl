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
Generic Design For Test Types.
"""

import ucdp as u


class TestModeType(u.AEnumType):
    """
    Test Mode.

    General Chip Test Mode.

        >>> for item in TestModeType().values(): print(item)
        EnumItem(0, 'func', doc=Doc(title='Functional Mode'))
        EnumItem(1, 'test', doc=Doc(title='Test Mode'))
    """

    keytype: u.BitType = u.BitType()

    comment: str = "Test Mode"

    def _build(self) -> None:
        self._add(0, "func", "Functional Mode")
        self._add(1, "test", "Test Mode")


class ScanModeType(u.AEnumType):
    """
    Scan Mode.

    Scan Mode of Digital Logic.

        >>> for item in ScanModeType().values(): print(item)
        EnumItem(0, 'func', doc=Doc(title='Functional Mode'))
        EnumItem(1, 'scan', doc=Doc(title='Scan Mode'))
    """

    keytype: u.BitType = u.BitType()

    comment: str = "Logic Scan-Test Mode"

    def _build(self) -> None:
        self._add(0, "func", "Functional Mode")
        self._add(1, "scan", "Scan Mode")


class ScanShiftType(u.AEnumType):
    """
    Scan Shift.

    Shift Mode During Digital Logic Test.

        >>> for item in ScanShiftType().values(): print(item)
        EnumItem(0, 'capture', doc=Doc(title='Capture Phase during Scan Mode'))
        EnumItem(1, 'shift', doc=Doc(title='Shift Phase during Scan Mode'))
    """

    keytype: u.BitType = u.BitType()

    comment: str = "Scan Shift Phase"

    def _build(self) -> None:
        self._add(0, "capture", "Capture Phase during Scan Mode")
        self._add(1, "shift", "Shift Phase during Scan Mode")


class MbistModeType(u.AEnumType):
    """
    Memory BIST Mode.

        >>> for item in MbistModeType().values(): print(item)
        EnumItem(0, 'func', doc=Doc(title='Functional Mode'))
        EnumItem(1, 'mbist', doc=Doc(title='Memory BIST Mode'))
    """

    keytype: u.BitType = u.BitType()

    comment: str = "Memory Built-In Self-Test"

    def _build(self) -> None:
        self._add(0, "func", "Functional Mode")
        self._add(1, "mbist", "Memory BIST Mode")


class DftModeType(u.AStructType):
    """
    DFT Modes.

        >>> for item in DftModeType().values(): print(item)
        StructItem('test_mode', TestModeType(), doc=Doc(title='Test Mode'...))
        StructItem('scan_mode', ScanModeType(), doc=Doc(title='Scan Mode'...))
        StructItem('scan_shift', ScanShiftType(), doc=Doc(title='Scan Shift'...))
        StructItem('mbist_mode', MbistModeType(), doc=Doc(title='Memory BIST Mode'...))
    """

    comment: str = "Test Control"

    def _build(self) -> None:
        self._add("test_mode", TestModeType(), title="Test Mode")
        self._add("scan_mode", ScanModeType(), title="Scan Mode")
        self._add("scan_shift", ScanShiftType(), title="Scan Shift")
        self._add("mbist_mode", MbistModeType(), title="Memory BIST Mode")


class JtagType(u.AStructType):
    """
    JTAG Type.

        >>> for item in JtagType().values(): print(item)
        StructItem('tms', BitType())
        StructItem('trst', BitType())
        StructItem('tdi', BitType())
        StructItem('tck', BitType())
        StructItem('tdo', BitType(), orientation=BWD)
        StructItem('tdo_oe_n', BitType(), orientation=BWD)
    """

    def _build(self) -> None:
        self._add("tms", u.BitType(), u.FWD)
        self._add("trst", u.BitType(), u.FWD)
        self._add("tdi", u.BitType(), u.FWD)
        self._add("tck", u.BitType(), u.FWD)
        self._add("tdo", u.BitType(), u.BWD)
        self._add("tdo_oe_n", u.BitType(), u.BWD)


class ScanDataType(u.AStructType):
    """
    Scan Data.

        >>> for item in ScanDataType().values(): print(item)
        StructItem('si0', BitType())
        StructItem('si1', BitType())
        StructItem('si2', BitType())
        StructItem('si3', BitType())
        StructItem('si4', BitType())
        StructItem('si5', BitType())
        StructItem('si6', BitType())
        StructItem('si7', BitType())
        StructItem('so0', BitType(), orientation=BWD)
        StructItem('so1', BitType(), orientation=BWD)
        StructItem('so2', BitType(), orientation=BWD)
        StructItem('so3', BitType(), orientation=BWD)
        StructItem('so4', BitType(), orientation=BWD)
        StructItem('so5', BitType(), orientation=BWD)
        StructItem('so6', BitType(), orientation=BWD)
        StructItem('so7', BitType(), orientation=BWD)

    """

    comment: str = "Scan Chain Data"
    width: int = 8

    def _build(self) -> None:
        for idx in range(self.width):
            self._add(f"si{idx}", u.BitType(), u.FWD)
        for idx in range(self.width):
            self._add(f"so{idx}", u.BitType(), u.BWD)
