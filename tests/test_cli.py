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
"""Test Command-Line-Interface."""

from click.testing import CliRunner
from pytest import fixture
from ucdp.cli import ucdp


@fixture
def runner():
    """Click Runner for Testing."""
    yield CliRunner()


def _assert_output(result, lines):
    assert [line.rstrip() for line in result.output.splitlines()] == lines


def test_lsaddrmap(runner, testdata_path):
    """Lsaddrmap Command."""
    result = runner.invoke(ucdp, ["lsaddrmap", "top_lib.top"])
    assert result.exit_code == 0
    lines = [
        "",
        "",
        "Size: 268 KB",
        "",
        "| Namespace | Type | Base    | Size           | Attributes |",
        "| --------- | ---- | ----    | ----           | ---------- |",
        "| one       | -    | 0x11000 | 512x32 (2 KB)  |            |",
        "| two       | -    | 0x12000 | 1024x32 (4 KB) |            |",
        "| one       | -    | 0x41000 | 512x32 (2 KB)  |            |",
        "| two       | -    | 0x42000 | 1024x32 (4 KB) |            |",
        "",
    ]
    _assert_output(result, lines)

    result = runner.invoke(ucdp, ["lsaddrmap", "top_lib.top", "--full"])
    assert result.exit_code == 0
    lines = [
        "",
        "",
        "Size: 268 KB",
        "",
        "| Namespace | Type | Base    | Size           | Attributes |",
        "| --------- | ---- | ----    | ----           | ---------- |",
        "| one       | -    | 0x11000 | 512x32 (2 KB)  |            |",
        "| two       | -    | 0x12000 | 1024x32 (4 KB) |            |",
        "| one       | -    | 0x41000 | 512x32 (2 KB)  |            |",
        "| two       | -    | 0x42000 | 1024x32 (4 KB) |            |",
        "",
        "",
        "| Addrspace | Word  | Field  | Offset   | Access | Reset | Attributes |",
        "| --------- | ----  | -----  | ------   | ------ | ----- | ---------- |",
        "| one       |       |        | 0x11000  |        |       |            |",
        "| one       | word0 |        |   +4     |        |       |            |",
        "| one       | word0 | field0 |     3:0  | RW/-   | 0x0   |            |",
        "| two       |       |        | 0x12000  |        |       |            |",
        "| two       | word1 |        |   +1008  |        |       |            |",
        "| two       | word1 | field1 |     31:0 | RO/-   | 0x0   | CONST      |",
        "| one       |       |        | 0x41000  |        |       |            |",
        "| one       | word0 |        |   +4     |        |       |            |",
        "| one       | word0 | field0 |     3:0  | RW/-   | 0x0   |            |",
        "| two       |       |        | 0x42000  |        |       |            |",
        "| two       | word1 |        |   +1008  |        |       |            |",
        "| two       | word1 | field1 |     31:0 | RO/-   | 0x0   | CONST      |",
        "",
    ]
    _assert_output(result, lines)
