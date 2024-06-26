#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
from typing import TextIO
import sys

MAX_POSITION = 255
MAX_OPERAND = 255

OPCODES = {
    # Simple opcodes
    "a2p":  (0b01001000, False),
    "add":  (0b00110100, True),
    "addi": (0b00110110, True),
    "addp": (0b00110101, False),
    "clm":  (0b10000000, True),
    "clmp": (0b10000001, False),
    "jc":   (0b00000010, True),
    "jcp":  (0b00000011, False),
    "jev":  (0b00011110, True),
    "jevp": (0b00011111, True),
    "jmp":  (0b00000000, True),
    "jnc":  (0b00010010, True),
    "jncp": (0b00010011, False),
    "jnop": (0b00011111, False),
    "jns":  (0b00011010, True),
    "jnsp": (0b00011011, False),
    "jnz":  (0b00010110, True),
    "jnzp": (0b00010111, False),
    "jod":  (0b00001110, True),
    "jodp": (0b00001111, False),
    "jp":   (0b00000001, False),
    "js":   (0b00001010, True),
    "jsp":  (0b00001011, False),
    "jz":   (0b00000110, True),
    "jzp":  (0b00000111, False),
    "la":   (0b00100000, True),
    "lai":  (0b00100010, True),
    "lap":  (0b00100001, False),
    "lp":   (0b01000000, True),
    "lpi":  (0b01000010, True),
    "lpp":  (0b01000001, False),
    "nor":  (0b00111000, True),
    "nori": (0b00111010, True),
    "norp": (0b00111001, False),
    "nop":  (0b00101000, False),
    "shr":  (0b00110000, False),
    "shrs": (0b10010000, True),
    "sta":  (0b10001000, True),
    "stap": (0b10001001, False),
    "stip": (0b10000011, True),
    "sub":  (0b00111100, True),
    "subi": (0b00111110, True),
    "subp": (0b00111101, False),

    # For convenience, valid after la x; sub y; checks x <=> y
    "jge":  (0b00000010, True),
    "jl":   (0b00010010, True),
}

@dataclass
class Numeral:
    value: int

@dataclass
class Ref:
    name: str

Operand = None | Numeral | Ref

@dataclass
class Instruction:
    lineno: int
    opcode: str
    operand: Operand
    position: int = -1

@dataclass
class EquDirective:
    lineno: int
    name: str
    value: Operand

@dataclass
class LabelDirective:
    lineno: int
    name: str
    value: int = -1

@dataclass
class PositionDirective:
    lineno: int
    value: int

Statement = Instruction | EquDirective | LabelDirective | PositionDirective


class Assembler:
    ERROR_LABEL = "__error__"

    def __init__(self, infile: TextIO) -> None:
        self.infile = infile
        self.has_error: bool = False
        self.parser_line: int = -1
        self.errors: list[str] = []


    def emit_parser_error(self, message: str) -> None:
        self.errors.append(f"line {self.parser_line}: {message}")
        self.has_error = True


    def emit_error_about(self, statement: Statement, message: str) -> None:
        self.errors.append(f"line {statement.lineno}: {message}")
        self.has_error = True


    def report_errors(self) -> bool:
        if self.has_error:
            for error in self.errors:
                print(error, file=sys.stderr)

        return self.has_error


    def strip_comments(self, line: str) -> str:
        (line, _, _) = line.partition(";")
        (line, _, _) = line.partition("#")
        return line


    def parse_operand(self, operand: str) -> Operand:
        if operand.isidentifier():
            return Ref(operand)
        else:
            try:
                value = int(operand, 0)
                return Numeral(value)
            except ValueError:
                self.emit_parser_error(f"\"{value}\" is neither a valid label name nor a numeral")
                return None


    def parse_line(self, line: str) -> list[Statement]:
        line = self.strip_comments(line)
        words = line.split()

        if len(words) == 0:
            return []

        opcode = words[0]
        match opcode:
            case ".equ":
                if len(words) != 3:
                    self.emit_parser_error(f".equ directive expects 2 arguments, but {len(words) - 1} were given")
                    return []

                [_, label, value] = words
                if not label.isidentifier():
                    self.emit_parser_error(f"\"{label}\" is not a valid label name")
                    label = Assembler.ERROR_LABEL

                operand = self.parse_operand(value)
                return [EquDirective(lineno = self.parser_line, name = label, value = operand)]

            case ".pos":
                if len(words) != 2:
                    self.emit_parser_error(f".pos directive expects 1 argument, but {len(words) - 1} were given")
                    return []

                [_, value] = words
                try:
                    return [PositionDirective(lineno = self.parser_line, value = int(value, 0))]
                except ValueError:
                    self.emit_parser_error(f"\"{value}\" is not a valid numeral")

        maybe_label = []

        if opcode.endswith(":"):
            label = opcode[:-1]

            if not label.isidentifier():
                self.emit_parser_error(f"\"{label}\" is not a valid label name")
                label = Assembler.ERROR_LABEL

            maybe_label.append(LabelDirective(lineno = self.parser_line, name = label))

            words = words[1:]

        if len(words) == 0:
            return maybe_label

        if len(words) == 1:
            [opcode] = words
            operand = None
        elif len(words) == 2:
            [opcode, operand_word] = words
            operand = self.parse_operand(operand_word)
        else:
            self.emit_parser_error(f"an instruction expects at most one argument, but {len(words) - 1} were given")

        return maybe_label + [Instruction(lineno = self.parser_line, opcode = opcode, operand = operand)]


    def parse_file(self, f: TextIO) -> list[Statement]:
        statements: list[Statement] = []

        for (i, line) in enumerate(f):
            self.parser_line = i

            statements += self.parse_line(line)

        return statements


    def layout_statements(self, statements: list[Statement]) -> None:
        pos = 0
        for s in statements:
            match s:
                case Instruction():
                    if pos > MAX_POSITION:
                        self.emit_error_about(s, f"statement placed outside program memory (requested position {pos}, but maximum is {MAX_POSITION})")
                    s.position = pos
                    pos += 1
                case LabelDirective():
                    s.value = pos
                case PositionDirective(value=value):
                    pos = value


    def collect_labels(self, statements: list[Statement]) -> dict[str, int]:
        labels: dict[str, int] = {}

        for s in statements:
            match s:
                case EquDirective(_, name, value):
                    if name in labels:
                        self.emit_error_about(s, f"label \"{name}\" redefined")

                    match value:
                        case Numeral(value):
                            labels[name] = value
                        case Ref(ref_name):
                            if ref_name not in labels:
                                self.emit_error_about(s, f".equ directive references unknown label \"{ref_name}\"")
                                labels[name] = -1
                            else:
                                labels[name] = labels[ref_name]

                case LabelDirective(_, name, value):
                    if name in labels:
                        self.emit_error_about(s, f"label \"{name}\" redefined")

                    labels[name] = value

        return labels


    def resolve_references(self, statements: list[Statement], labels: dict[str, int]) -> None:
        for s in statements:
            if isinstance(s, Instruction) and isinstance(s.operand, Ref):
                ref = s.operand.name
                if ref not in labels:
                    self.emit_error_about(s, f"label \"{ref}\" is not defined")
                else:
                    s.operand = Numeral(value = labels[ref])


    def emit_instructions(self, statements: list[Statement]) -> list[int]:
        # The instruction 0x00ff encodes "jmp 0xff", so we fill the memory
        # with jumps to the last address. This means that any jump to an
        # invalid location will stall the program at address 0xff.
        memory_image: list[int] = [0x00ff for _ in range(256)]

        for s in statements:
            if isinstance(s, Instruction):
                opcode = s.opcode
                operand = s.operand
                position = s.position

                try:
                    (encoding, has_operand) = OPCODES[opcode]
                except KeyError:
                    self.emit_error_about(s, f"instruction \"{opcode}\" is not known")
                    continue

                if has_operand and operand is None:
                    self.emit_error_about(s, f"instruction \"{opcode}\" expects an operand, but none was given")
                    continue
                if not has_operand and operand is not None:
                    self.emit_error_about(s, f"instruction \"{opcode}\" does not expect an operand, but one was given")
                    continue

                code = encoding << 8
                if operand is not None:
                    assert isinstance(operand, Numeral)

                    val = operand.value
                    if val > MAX_OPERAND:
                        self.emit_error_about(s, f"operand {val} is too large (maximum is {MAX_OPERAND})")
                        val = 0xff
                    code |= operand.value

                assert 0 <= code <= 0xffff

                memory_image[position] = code

        return memory_image


    def assemble(self) -> list[int] | None:
        statements = self.parse_file(self.infile)
        if self.report_errors():
            return None

        self.layout_statements(statements)
        if self.report_errors():
            return None

        labels = self.collect_labels(statements)
        if self.report_errors():
            return None

        self.resolve_references(statements, labels)
        if self.report_errors():
            return None

        memory_image = self.emit_instructions(statements)
        if self.report_errors():
            return None

        return memory_image


def assemble_file(file: TextIO) -> list[int] | None:
    a = Assembler(file)
    return a.assemble()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="assembler.py",
        description="Assembler for the Vis Vitalis relay processor")
    parser.add_argument("input_file",
                        metavar="input-file",
                        nargs="?",
                        help="defaults to stdin when not given")
    parser.add_argument("-o", "--output-file",
                        help="default to stdout when not given")
    args = parser.parse_args()

    infile: TextIO
    if args.input_file:
        infile = open(args.input_file, encoding="utf-8")
    else:
        infile = sys.stdin
        print("Reading from stdin. Hint: Type EOF (^D) to finish the input.", file=sys.stderr)

    memory_image = assemble_file(infile)

    if memory_image:
        outfile: TextIO
        if args.output_file:
            outfile = open(args.output_file, "w", encoding="utf-8")
        else:
            outfile = sys.stdout

        outfile.write(" ")
        for (i, word) in enumerate(memory_image):
            outfile.write(f"{word:04x} ")
            if i % 16 == 15:
                outfile.write("\n ")
