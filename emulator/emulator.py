#!/usr/bin/env python3

import argparse
from cmd import Cmd
import sys

# Bit widths of our memories
PROGRAM_SIZE = 1 << 8
PROGRAM_MAX = 1 << 16
DATA_SIZE = 256
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

# Shell stuff
USE_ANSI = True
if USE_ANSI:
    REVERSE_VIDEO = "\033[7m"
    NORMAL_VIDEO = "\033[m"
else:
    REVERSE_VIDEO = ""
    NORMAL_VIDEO = ""

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
        # We range check the whole program beforehand so we don't end
        # up with half of it written to memory.
        self.range_check("data start", start, DATA_SIZE)
        self.range_check("data end", start + len(words) - 1, DATA_SIZE)
        for (address, data) in enumerate(words, start=start):
            self.store_data(address, data)


    def zero_flag(self) -> bool:
        return self.register_a == 0


    def sign_flag(self) -> bool:
        return self.register_a & 0b10000000 != 0


    def odd_flag(self) -> bool:
        return self.register_a & 0b00000001 != 0


    def bitinvert(self, x) -> int:
        return ~x & 0xff


    def step(self) -> None:
        instruction = self.program_memory[self.program_counter]
        if instruction & ((1 << WRITE_A_BIT) | (1 << WRITE_P_BIT) | (1 << WRITE_MEMORY_BIT)) == 0:
            self.step_jump(instruction)
        else:
            self.step_compute(instruction)

        self.clock += 1


    def step_compute(self, instruction) -> None:
        insn_address_source = instruction & (1 << ADDRESS_SOURCE_BIT) != 0
        insn_operand_source = instruction & (1 << OPERAND_SOURCE_BIT) != 0
        insn_add = instruction & (1 << ADD_BIT) != 0
        insn_invert = instruction & (1 << INVERT_BIT) != 0
        insn_result_source_1 = instruction & (1 << RESULT_SOURCE_1_BIT) != 0
        insn_result_source_2 = instruction & (1 << RESULT_SOURCE_2_BIT) != 0
        insn_write_a = instruction & (1 << WRITE_A_BIT) != 0
        insn_write_p = instruction & (1 << WRITE_P_BIT) != 0
        insn_write_memory = instruction & (1 << WRITE_MEMORY_BIT) != 0

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

        non_adder_result = self.bitinvert(self.register_a | alu_in_2) if insn_invert else self.register_a >> 1
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


    def step_jump(self, instruction) -> None:
        insn_address_source = instruction & (1 << ADDRESS_SOURCE_BIT) != 0
        insn_conditional = instruction & (1 << CONDITIONAL_BIT) != 0
        insn_condition_1 = instruction & (1 << CONDITION_1_BIT) != 0
        insn_condition_2 = instruction & (1 << CONDITION_2_BIT) != 0
        insn_condition_invert = instruction & (1 << CONDITION_INVERT_BIT) != 0

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


class Shell(Cmd):
    intro = "This is the vis vitalis emulator. Type help or ? to list the commands.\n" \
        "Note: All numbers are hexadecimal by default. Prefix decimal numbers with \"0d\"\n"
    prompt = "> "

    def initialize(self):
        self.machine = Machine()
        self.hex_mode = True


    def to_int(self, string: str) -> int:
        if string.startswith("0d"):
            return int(string[2:], 10)
        elif string.startswith(("0b", "0B", "0o", "0O", "0x", "0X")):
            return int(string, 0)
        else:
            return int(string, 16)


    def do_exit(self, arg: str) -> bool:
        "exit the emulator"
        return True


    def do_EOF(self, arg: str) -> bool:
        "exit the emulator"
        print()
        return self.do_exit(arg)


    def do_pwrite(self, arg: str) -> None:
        "pwrite <start> <data ...>: Write <data ...> into program memory beginning at address <start>"
        try:
            [address_word, *data_words] = arg.split()
            address = self.to_int(address_word)
            data = list(map(self.to_int, data_words))
            self.machine.write_program(address, data)
        except ValueError as e:
            print(f"Failed: {e}")


    def do_dwrite(self, arg: str) -> None:
        "dwrite <start> <data ...>: Write <data ...> into data memory beginning at address <start>"
        try:
            [address_word, *data_words] = arg.split()
            address = self.to_int(address_word)
            data = list(map(self.to_int, data_words))
            self.machine.write_data(address, data)
        except ValueError as e:
            print(f"Failed: {e}")


    def load_from_file(self, arg: str, next_command: str) -> None:
        try:
            words = arg.split()
            filename = words[0]

            if len(words) == 1:
                start = "0"
            elif len(words) == 2:
                start = words[1]
            else:
                raise ValueError("too many arguments (expected 1 or 2)")

            contents = open(filename).read().replace("\n", " ")
            self.cmdqueue.append(f"{next_command} {start} {contents}")

        except Exception as e:
            print(f"Failed: {e}")


    def do_pload(self, arg: str) -> None:
        "pload <filename> <start>?: Load program memory from a file named <filename>. Begin at address <start>, or at address 0 if no <start> is given."
        self.load_from_file(arg, "pwrite")


    def do_dload(self, arg: str) -> None:
        "dload <filename> <start>?: Load data memory from a file named <filename>. Begin at address <start>, or at address 0 if no <start> is given."
        self.load_from_file(arg, "dwrite")


    def do_reg(self, arg: str) -> None:
        "reg <reg> <value>: Set register <reg> to value <value>. Register names are case-insensitive."
        try:
            words = arg.split()
            regname = words[0].casefold()
            value = self.to_int(words[1])

            match regname:
                case "a":
                    self.machine.register_a = value
                case "p":
                    self.machine.register_p = value
                case "pc":
                    self.machine.program_counter = value
                case _:
                    raise ValueError(f"{regname} is not a valid register name")

        except Exception as e:
            print(f"Failed: {e}")


    def do_reset(self, arg: str) -> None:
        "reset: Reset program counter and clock to 0"
        self.machine.program_counter = 0
        self.machine.clock = 0


    def do_show(self, arg: str) -> None:
        "show: Show current machine state"

        print("PROGRAM MEMORY (highlight: PC) ================================================")
        for (i, word) in enumerate(self.machine.program_memory):
            if i == self.machine.program_counter:
                print(REVERSE_VIDEO, end="")
            print(f"{word:04x}", end="")
            if i == self.machine.program_counter:
                print(NORMAL_VIDEO, end="")
            if i % 16 == 15:
                print()
            else:
                print(" ", end="")
        print("===============================================================================")
        print()
        print("DATA MEMORY (highlight: P) ====================")
        for (i, word) in enumerate(self.machine.data_memory):
            if i == self.machine.register_p:
                print(REVERSE_VIDEO, end="")
            print(f"{word:02x}", end="")
            if i == self.machine.register_p:
                print(NORMAL_VIDEO, end="")
            if i % 16 == 15:
                print()
            else:
                print(" ", end="")
        print("===============================================")
        print()
        print(f"A     = {self.machine.register_a:02x}")
        print(f"P     = {self.machine.register_p:02x}")
        print(f"PC    = {self.machine.program_counter:02x}")
        print("FLAGS = ", end="")
        print("ZERO "  if self.machine.zero_flag() else "     ",  end="")
        print("SIGN "  if self.machine.sign_flag() else "     ",  end="")
        print("ODD "   if self.machine.odd_flag()  else "    ",   end="")
        print("CARRY " if self.machine.carry_flag  else "      ")
        print()
        print(f"CLOCK = {self.machine.clock}")


    def do_step(self, arg: str) -> None:
        "step the machine by one instruction. Also the default action if no command is given."
        self.machine.step()
        self.cmdqueue.append("show")


    def emptyline(self) -> None:
        return self.do_step("")


    def do_test(self, arg: str) -> None:
        self.cmdqueue.append("pload ../programs/out/listmax.o")
        self.cmdqueue.append("dload ../programs/out/listmaxtest.dat")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("program_image", nargs="?", default=None)
    args = parser.parse_args()

    shell = Shell()
    shell.initialize()

    if args.program_image is not None:
        shell.cmdqueue.append(f"pload {args.program_image}")

    shell.cmdloop()
