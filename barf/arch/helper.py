# Copyright (c) 2014, Fundacion Dr. Manuel Sadosky
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from barf.arch.arm.armbase import ArmImmediateOperand
from barf.arch.x86.x86base import X86ImmediateOperand

from hexagondisasm.common import HexagonInstruction
from hexagondisasm.common import InstructionImmediate
from hexagondisasm.common import InstructionRegister

def extract_branch_target(asm_instruction):
    address = None

    if isinstance(asm_instruction, HexagonInstruction):
        return extract_hexagon_target(asm_instruction)

    target_oprnd = asm_instruction.operands[0]
    if isinstance(target_oprnd, X86ImmediateOperand) or \
       isinstance(target_oprnd, ArmImmediateOperand):
        address = target_oprnd.immediate

    return address

def extract_call_target(asm_instruction):
    address = None

    if isinstance(asm_instruction, HexagonInstruction):
        return extract_hexagon_target(asm_instruction)

    target_oprnd = asm_instruction.operands[0]
    if isinstance(target_oprnd, X86ImmediateOperand) or \
       isinstance(target_oprnd, ArmImmediateOperand):
        address = target_oprnd.immediate

    return address

def extract_hexagon_target(inst):
    if inst.template and inst.template.branch:
        branch = inst.template.branch

        if branch.target is None:
            # TODO: Hexagon issue: the LR case is not being handle correctly
            # return 'LR'
            return None

        target_operand = inst.get_real_operand(branch.target)

        if isinstance(target_operand, InstructionImmediate):
            return int(target_operand.value)
            # The int conversion is needed, otherwise a long is returned and pydot fails when saving the CFG.

        if isinstance(target_operand, InstructionRegister):
            # return target_operand.name
            return None

    raise
    # TODO: Check when this could happen.
