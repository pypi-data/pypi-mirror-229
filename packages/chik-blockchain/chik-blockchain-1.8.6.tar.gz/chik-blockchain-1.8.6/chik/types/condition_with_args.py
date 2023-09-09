from __future__ import annotations

from dataclasses import dataclass
from typing import List

from chik.types.condition_opcodes import ConditionOpcode
from chik.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class ConditionWithArgs(Streamable):
    """
    This structure is used to store parsed KLVM conditions
    Conditions in KLVM have either format of (opcode, var1) or (opcode, var1, var2)
    """

    opcode: ConditionOpcode
    vars: List[bytes]
