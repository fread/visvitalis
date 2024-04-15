#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import os

OPCODES = {
    "jmp":  (0b00000000, True),
    "clm":  (0b00000001, True),
    "lp":   (0b00000010, True),
    "la":   (0b00000100, True),
    "shr":  (0b00001100, False),
    "sta":  (0b00010001, True),
    "a2p":  (0b00010010, False),
    "nor":  (0b00011100, True),
    "add":  (0b00101100, True),
    "sub":  (0b00111100, True),
    "jc":   (0b01000000, True),
    "lpi":  (0b01000010, True),
    "lai":  (0b01000100, True),
    "jnc":  (0b01001000, True),
    "js":   (0b01010000, True),
    "jns":  (0b01011000, True),
    "nori": (0b01011100, True),
    "jz":   (0b01100000, True),
    "jnz":  (0b01101000, True),
    "addi": (0b01101100, True),
    "jod":  (0b01110000, True),
    "jev":  (0b01111000, True),
    "subi": (0b01111100, True),
    "jp":   (0b10000000, False),
    "clmp": (0b10000001, False),
    "lpp":  (0b10000010, False),
    "lap":  (0b10000100, False),
    "stap": (0b10010001, False),
    "norp": (0b10011100, False),
    "addp": (0b10101100, False),
    "subp": (0b10111100, False),
    "jcp":  (0b11000000, False),
    "stip": (0b11000001, True),
    "jncp": (0b11001000, False),
    "jsp":  (0b11010000, False),
    "jnsp": (0b11011000, False),
    "jzp":  (0b11100000, False),
    "jnzp": (0b11101000, False),
    "jop":  (0b11110000, False),
    "jnop": (0b11111000, False),
}

@dataclass
class Numeral:
    value: int

@dataclass
class Ref:
    name: str

Argument = None | Numeral | Ref

@dataclass
class Instruction:
    lineno: int
    opcode: str
    argument: Argument
    position: int = -1

@dataclass
class EquDirective:
    lineno: int
    name: str
    value: Argument

@dataclass
class LabelDirective:
    lineno: int
    name: str
    value: int = -1

@dataclass
class PositionDirective:
    lineno: int
    value: int

@dataclass
class ParseError:
    message: str

Statement = Instruction | EquDirective | LabelDirective | PositionDirective | ParseError


def strip_comments(string):
    (string, _, _) = string.partition(";")
    (string, _, _) = string.partition("#")
    return string


def emit_error_at(i, error):
    return ParseError(message = f"line {i}: {error}")


def parse_argument(i, argument):
    if argument.isidentifier():
        return Ref(argument)
    else:
        try:
            value = int(argument, 0)
            return Numeral(value)
        except ValueError:
            return emit_error_at(i, f"\"{value}\" is neither a valid label name nor a numeral")


def parse_line(i, line):
    line = strip_comments(line)
    words = line.split()

    if len(words) == 0:
        return None

    opcode = words[0]
    match opcode:
        case ".equ":
            if len(words) != 3:
                return emit_error_at(i, f".equ directive expects 2 arguments, but {len(words) - 1} were given")

            [_, label, value] = words
            if not label.isidentifier():
                return emit_error_at(i, f"\"{label}\" is not a valid label name")

            argument = parse_argument(i, value)
            if type(argument) is ParseError:
                return argument
            else:
                return EquDirective(lineno = i, name = label, value = argument)

        case ".l":
            if len(words) != 2:
                return emit_error_at(i, f".l directive expects 1 argument, but {len(words) - 1} were given")

            [_, label] = words
            if not label.isidentifier():
                return emit_error_at(i, f"\"{label}\" is not a valid label name")

            return LabelDirective(lineno = i, name = label)

        case ".pos":
            if len(words) != 2:
                return emit_error_at(i, f".pos directive expects 1 argument, but {len(words) - 1} were given")

            [_, value] = words
            try:
                value = int(argument, 0)
                return PositionDirective(lineno = i, value = value)
            except ValueError:
                return emit_error_at(i, f"\"{value}\" is neither a valid label name nor a numeral")

    # Else assume a normal instruction
    if len(words) > 2:
        return emit_error_at(i, f"an instruction expects at most one argument, but {len(words) - 1} were given")

    if len(words) == 1:
        [opcode] = words
        argument = None
    elif len(words) == 2:
        [opcode, argument] = words
        argument = parse_argument(i, argument)
        if type(argument) is ParseError:
            return argument

    return Instruction(lineno = i, opcode = opcode, argument = argument)


def parse_file(f):
    statements = []
    have_error = False

    for (i, line) in enumerate(f):
        parsed = parse_line(i, line)

        if parsed is not None:
            statements.append(parsed)

        if type(parsed) is ParseError:
            have_error = True

    if have_error:
        for s in statements:
            if type(s) is ParseError:
                print(s.message)

        return None

    return statements


def layout_statements(statements):
    pos = 0
    for s in statements:
        match s:
            case Instruction():
                s.position = pos
                pos += 1
            case LabelDirective():
                s.value = pos
            case PositionDirective(value):
                pos = value


def collect_labels(statements):
    labels = {}
    have_error = False

    for s in statements:
        match s:
            case EquDirective(lineno, name, value):
                if name in labels:
                    print(f"line {lineno}: label {name} redefined")
                    have_error = True

                match value:
                    case Numeral(value):
                        labels[name] = value
                    case Ref(ref_name):
                        if ref_name not in labels:
                            print(f"line {lineno}: .equ directive references unknown label {ref_name}")
                            have_error = True
                            labels[name] = -1
                        else:
                            labels[name] = labels[ref_name]

            case LabelDirective(lineno, name, value):
                if name in labels:
                    print(f"line {lineno}: label {name} redefined")
                    have_error = True

                labels[name] = value

    if have_error:
        return None
    else:
        return labels


def resolve_references(statements, labels):
    have_error = False

    for s in statements:
        if type(s) is Instruction and type(s.argument) is Ref:
            ref = s.argument.name
            if ref not in labels:
                print(f"line {lineno}: label {name} is not defined")
                have_error = True
            else:
                s.argument = Numeral(value = labels[ref])

    return have_error


def emit_instructions(statements):
    # The instruction 0x00ii encodes "jmp i", so we fill the memory
    # with self-jumps. This means that any jump to an invalid location
    # will stall the program.
    memory_image = [i for i in range(256)]
    have_error = False

    for s in statements:
        if type(s) is Instruction:
            lineno = s.lineno
            opcode = s.opcode
            argument = s.argument
            position = s.position

            if opcode not in OPCODES:
                print(f"line {lineno}: instruction \"{opcode}\" is not known")
                have_error = True
                continue

            (encoding, has_argument) = OPCODES[opcode]

            if has_argument and argument is None:
                print(f"line {lineno}: instruction \"{opcode}\" expects an argument, but none was given")
                have_error = True
                continue
            if not has_argument and argument is not None:
                print(f"line {lineno}: instruction \"{opcode}\" does not expect an argument, but one was given")
                have_error = True
                continue

            code = encoding << 8
            if argument is not None:
                assert type(argument) is Numeral
                code |= argument.value

            assert 0 <= code <= 0xffff

            memory_image[position] = code

    if have_error:
        return None
    else:
        return memory_image

def assemble_file(f):
    statements = parse_file(f)

    if statements is None:
        return None

    for s in statements:
        print(s)
    print()

    layout_statements(statements)
    labels = collect_labels(statements)
    if labels is None:
        return None
    have_error = resolve_references(statements, labels)
    if have_error:
        return None

    for s in statements:
        print(s)
    print()

    print(labels)

    return emit_instructions(statements)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="assembler.py",
        description="Assembler for the Vis Vitalis relay processor")
    parser.add_argument("input_file",
                        metavar="input-file",
                        nargs="?",
                        help="defaults to stdin when not given")
    parser.add_argument("-o", "--output-file")
    args = parser.parse_args()

    if args.input_file:
        infile = open(args.input_file, encoding="utf-8")
    else:
        infile = os.stdin
    memory_image = assemble_file(infile)

    if memory_image:
        for (i, word) in enumerate(memory_image):
            print(f"{word:04x} ", end="\n" if i % 16 == 15 else "")
