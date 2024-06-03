#!/usr/bin/env python3

import argparse
from cmd import Cmd
import sys

from machine import Machine

# Shell stuff
USE_ANSI = True
if USE_ANSI:
    REVERSE_VIDEO = "\033[7m"
    NORMAL_VIDEO = "\033[m"
else:
    REVERSE_VIDEO = ""
    NORMAL_VIDEO = ""

class Shell(Cmd):
    intro = "This is the vis vitalis emulator. Type help or ? to list the commands.\n" \
        "To step the machine, you may also simply press enter on an empty prompt\n" \
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="*", default=None)
    args = parser.parse_args()

    shell = Shell()
    shell.initialize()

    if len(args.images) > 2:
        print("Too many image files were given. Expecting either:")
        print("  - Just a program image")
        print("  - First a program image, then a data image")
        sys.exit(1)

    elif len(args.images) == 2:
        [program_image, data_image] = args.images
        shell.cmdqueue.append(f"pload {program_image}")
        shell.cmdqueue.append(f"dload {data_image}")

    elif len(args.images) == 1:
        [program_image] = args.images
        shell.cmdqueue.append(f"pload {program_image}")

    shell.cmdloop()
