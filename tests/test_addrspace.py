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
"""Test Address Space."""

import re

import ucdp as u
from pytest import fixture, raises
from test2ref import assert_refdata
from ucdp_glbl.addrspace import ACCESSES, RO, RW, Addrspace, Word, get_is_const, get_is_volatile


@fixture
def word():
    """Example Word."""
    yield Word(name="word", offset=0, width=32)


@fixture
def addrspace():
    """Example Address Space."""
    yield Addrspace(name="name", depth=32)


def test_accesses(tmp_path, capsys):
    """Test Accesses."""
    for access in ACCESSES:
        print(str(access), repr(access))
        print(f"    title={access.title!r}")
        print(f"    descr={access.descr!r}")
    assert_refdata(test_accesses, tmp_path, capsys=capsys)


def test_add_field(addrspace, word):
    """Add Field."""
    field0 = word.add_field("field0", u.UintType(20), "RW")
    assert field0.name == "field0"
    assert field0.type_ == u.UintType(20)
    assert field0.bus == RW
    assert field0.core == RO
    assert field0.offset == 0
    assert field0.slice == u.Slice("19:0")
    assert field0.access == "RW/RO"

    field1 = word.add_field("field1", u.SintType(6), "RO", core="RO")
    assert field1.name == "field1"
    assert field1.type_ == u.SintType(6)
    assert field1.bus == RO
    assert field1.core == RO
    assert field1.offset == 20
    assert field1.slice == u.Slice("25:20")
    assert field1.access == "RO/RO"

    assert tuple(word.fields) == (field0, field1)

    field2 = word.add_field("field2", u.UintType(2), "RO", align=4)
    assert field2.name == "field2"
    assert field2.type_ == u.UintType(2)
    assert field2.bus == RO
    assert field2.core == RW
    assert field2.offset == 28
    assert field2.slice == u.Slice("29:28")
    assert field2.access == "RO/RW"

    with raises(ValueError, match=re.escape("Field 'field3' exceeds word width of 32")):
        word.add_field("field3", u.UintType(3), "RO", offset=30)

    field4 = word.add_field("field4", u.UintType(2), "RO", offset=30)
    assert field4.slice == u.Slice("31:30")

    assert tuple(word.fields) == (field0, field1, field2, field4)

    assert addrspace.get_field_hiername(word, field0) == "name.word.field0"
    assert addrspace.get_field_hiername(word, field1) == "name.word.field1"


def test_add_word(addrspace):
    """Add Word."""
    word0 = addrspace.add_word("word0")
    assert word0.name == "word0"
    assert word0.offset == 0
    assert word0.width == 32
    assert word0.depth is None
    assert word0.slice == u.Slice("0")

    word1 = addrspace.add_word("word1", offset=6)
    assert word1.name == "word1"
    assert word1.offset == 6
    assert word1.width == 32
    assert word1.depth is None
    assert word1.slice == u.Slice("6")

    word2 = addrspace.add_word("word2", align=4, depth=2)
    assert word2.name == "word2"
    assert word2.offset == 8
    assert word2.width == 32
    assert word2.depth == 2
    assert word2.slice == u.Slice("9:8")

    with raises(ValueError, match=re.escape("Word 'word3' exceeds address space depth of 32")):
        addrspace.add_word("word3", offset=32)

    word4 = addrspace.add_word("word4", offset=31)
    assert word4.name == "word4"
    assert word4.offset == 31
    assert word4.width == 32
    assert word4.depth is None
    assert word4.slice == u.Slice("31")

    assert tuple(addrspace.words) == (word0, word1, word2, word4)

    assert addrspace.get_word_hiername(word0) == "name.word0"
    assert addrspace.get_word_hiername(word1) == "name.word1"


def test_addrspace():
    """Address Space."""
    addrspace = Addrspace(name="name")
    assert addrspace.name == "name"
    assert addrspace.words == u.Namespace([])
    assert addrspace.width == 32
    assert addrspace.depth == 1024
    assert addrspace.size == u.Bytes("32 KB")


def test_addrspace_custom():
    """Address Space."""
    addrspace = Addrspace(name="name", width=64, depth=128)
    assert addrspace.name == "name"
    assert addrspace.words == u.Namespace([])
    assert addrspace.width == 64
    assert addrspace.depth == 128
    assert addrspace.size == u.Bytes("8 KB")


def test_lock():
    """Lock Mechanism."""
    addrspace = Addrspace(name="name")
    words = []
    for widx in range(3):
        word = addrspace.add_word(f"word{widx}")
        words.append(word)
        for fidx in range(3):
            word.add_field(f"field{fidx}", u.BitType(), "RO")

    assert addrspace.words.is_locked is False
    assert any(word.fields.is_locked for word in words) is False

    addrspace.lock()

    assert addrspace.words.is_locked is True
    assert all(word.fields.is_locked for word in words) is True


def test_volatile(tmp_path):
    """Test Volatile."""
    overview_file = tmp_path / "overview.txt"
    with overview_file.open("w", encoding="utf-8") as file:
        for bus in (None, *ACCESSES):
            for core in (None, *ACCESSES):
                is_volatile = " V" if get_is_volatile(bus, core) else "  "
                is_const = " Const" if get_is_const(bus, core) else " FF"
                busstr = (bus and bus.name) or "-"
                corestr = (core and core.name) or "-"
                file.write(f"{busstr:8s} {corestr:8s}{is_volatile}{is_const}\n")

    assert_refdata(test_volatile, tmp_path)
