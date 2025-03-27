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
Interrupt Types.
"""

import ucdp as u


class LevelIrqType(u.AEnumType):
    """
    Level IRQ.

        >>> import ucdp_glbl
        >>> irq = ucdp_glbl.irq.LevelIrqType()
        >>> irq
        LevelIrqType()
        >>> irq.width
        1
        >>> for item in irq.values(): print(item)
        EnumItem(0, 'idle')
        EnumItem(1, 'active')
    """

    keytype: u.BitType = u.BitType()

    comment: str = "Level IRQ"

    def _build(self) -> None:
        self._add(0, "idle")
        self._add(1, "active")


class ToggleIrqType(u.BitType):
    """
    Toggle IRQ.

        >>> import ucdp_glbl
        >>> irq = ucdp_glbl.irq.LevelIrqType()
        >>> irq
        LevelIrqType()
        >>> irq.width
        1
    """

    comment: str = "Toggle IRQ"
