# Bit widths of our memories
PROGRAM_SIZE = 1 << 8
PROGRAM_MAX = 1 << 16
DATA_SIZE = 1 << 8
DATA_MAX = 1 << 8

# Control bits for computational instructions
ADDRESS_SOURCE_BIT = 8
OPERAND_SOURCE_BIT = 9
ADD_BIT = 10
INVERT_BIT = 11
RESULT_SOURCE_1_BIT = 11
RESULT_SOURCE_2_BIT = 12
WRITE_A_BIT = 13
WRITE_P_BIT = 14
WRITE_MEMORY_BIT = 15
# ... and for jumps
CONDITIONAL_BIT = 9
CONDITION_1_BIT = 10
CONDITION_2_BIT = 11
CONDITION_INVERT_BIT = 12


class Machine:
    def __init__(self) -> None:
        self.program_memory: list[int] = [0x0000 for _ in range(PROGRAM_SIZE)]
        self.data_memory: list[int] = [0x00 for _ in range(DATA_SIZE)]

        self.program_counter: int = 0
        self.register_a: int = 0
        self.register_p: int = 0
        self.carry_flag: bool = False

        self.clock: int = 0


    def range_check(self, what: str, value: int, maximum: int) -> None:
        if value < 0 or value >= maximum:
            raise ValueError(f"{what} {value}/0x{value:x} is out of range (maximum is {maximum - 1}/0x{maximum - 1:x})")


    def store_program(self, address: int, data: int) -> None:
        self.range_check("address", address, PROGRAM_SIZE)
        self.range_check("data", data, PROGRAM_MAX)
        self.program_memory[address] = data


    def write_program(self, start: int, words: list[int]) -> None:
        # We range check the whole program beforehand so we don't end
        # up with half of it written to memory.
        self.range_check("program start", start, PROGRAM_SIZE)
        self.range_check("program end", start + len(words) - 1, PROGRAM_SIZE)
        for (address, data) in enumerate(words, start=start):
            self.store_program(address, data)


    def store_data(self, address: int, data: int) -> None:
        self.range_check("address", address, DATA_SIZE)
        self.range_check("data", data, DATA_MAX)
        self.data_memory[address] = data


    def write_data(self, start: int, words: list[int]) -> None:
        # We range check the whole data beforehand so we don't end
        # up with half of it written to memory.
        self.range_check("data start", start, DATA_SIZE)
        self.range_check("data end", start + len(words) - 1, DATA_SIZE)
        for (address, data) in enumerate(words, start=start):
            self.store_data(address, data)


    def set_program_counter(self, pc: int) -> None:
        self.range_check("program counter", pc, PROGRAM_SIZE)
        self.program_counter = pc


    def set_register_a(self, ra: int) -> None:
        self.range_check("register A", ra, DATA_MAX)
        self.register_a = ra


    def set_register_p(self, rp: int) -> None:
        self.range_check("register P", rp, DATA_MAX)
        self.register_p = rp


    def zero_flag(self) -> bool:
        return self.register_a == 0


    def sign_flag(self) -> bool:
        return self.register_a & 0b10000000 != 0


    def odd_flag(self) -> bool:
        return self.register_a & 0b00000001 != 0


    def bitinvert(self, x: int) -> int:
        return ~x & 0xff


    def is_bit_set(self, value: int, bit_index: int) -> bool:
        return value & (1 << bit_index) != 0


    def step(self) -> None:
        instruction = self.program_memory[self.program_counter]
        if instruction & ((1 << WRITE_A_BIT) |
                          (1 << WRITE_P_BIT) |
                          (1 << WRITE_MEMORY_BIT)) == 0:
            self.step_jump(instruction)
        else:
            self.step_compute(instruction)

        self.clock += 1


    def step_compute(self, instruction: int) -> None:
        insn_address_source = self.is_bit_set(instruction, ADDRESS_SOURCE_BIT)
        insn_operand_source = self.is_bit_set(instruction, OPERAND_SOURCE_BIT)
        insn_add = self.is_bit_set(instruction, ADD_BIT)
        insn_invert = self.is_bit_set(instruction, INVERT_BIT)
        insn_result_source_1 = self.is_bit_set(instruction, RESULT_SOURCE_1_BIT)
        insn_result_source_2 = self.is_bit_set(instruction, RESULT_SOURCE_2_BIT)
        insn_write_a = self.is_bit_set(instruction, WRITE_A_BIT)
        insn_write_p = self.is_bit_set(instruction, WRITE_P_BIT)
        insn_write_memory = self.is_bit_set(instruction, WRITE_MEMORY_BIT)

        operand = instruction & 0xff
        address = self.register_p if insn_address_source else operand
        memory_out = 0 if insn_write_memory else self.data_memory[address]
        operand_in = operand if insn_operand_source else memory_out

        alu_in_2 = self.bitinvert(operand_in) if insn_invert else operand_in
        carry_in = 1 if insn_invert else 0
        adder_result = self.register_a + alu_in_2 + carry_in
        carry_out = adder_result > 0xff
        adder_result &= 0xff
        if insn_add:
            self.carry_flag = carry_out

        non_adder_result = self.bitinvert(self.register_a | alu_in_2) \
            if insn_invert else self.register_a >> 1
        alu_result = adder_result if insn_add else non_adder_result

        intermediate_result = self.register_a if insn_result_source_1 else operand_in
        result = alu_result if insn_result_source_2 else intermediate_result

        if insn_write_a:
            self.register_a = result
        if insn_write_p:
            self.register_p = result
        if insn_write_memory:
            self.data_memory[address] = result

        self.program_counter += 1
        self.program_counter &= 0xff


    def step_jump(self, instruction: int) -> None:
        insn_address_source = self.is_bit_set(instruction, ADDRESS_SOURCE_BIT)
        insn_conditional = self.is_bit_set(instruction, CONDITIONAL_BIT)
        insn_condition_1 = self.is_bit_set(instruction, CONDITION_1_BIT)
        insn_condition_2 = self.is_bit_set(instruction, CONDITION_2_BIT)
        insn_condition_invert = self.is_bit_set(instruction, CONDITION_INVERT_BIT)

        operand = instruction & 0xff
        target = self.register_p if insn_address_source else operand

        if not insn_conditional:
            self.program_counter = target
        else:
            match (insn_condition_1, insn_condition_2):
                case (False, False):
                    flag = self.carry_flag
                case (False, True):
                    flag = self.sign_flag()
                case (True, False):
                    flag = self.zero_flag()
                case (True, True):
                    flag = self.odd_flag()

            # Jump if the flag in question is set and the jump
            # condition is not inverted or vice versa
            if flag != insn_condition_invert:
                self.program_counter = target
            else:
                self.program_counter += 1
                self.program_counter &= 0xff
