#!/usr/bin/env python3

import argparse
import itertools
from math import sqrt
import sys
from typing import Optional, List

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

import machine
from machine import Machine

ENTRY_FG_DEFAULT: str | None = None
ENTRY_BG_DEFAULT: str | None = None
ENTRY_DISABLED_BG_DEFAULT: str | None = None

class UI:
    def spacer(self, parent: Frame, row: int, col: int, width: int=20) -> None:
        Frame(parent, width=width).grid(row=row, column=col)

    def __init__(self, root: Tk):
        self.machine = Machine()

        self.is_locked = False

        self.frm = Frame(root)
        self.frm.pack()

        Label(self.frm, text="Program Memory").grid(row=0, column=0)

        frm_progmem_buttons = Frame(self.frm)
        frm_progmem_buttons.grid(row=1, column=0)

        self.btn_load_prog = Button(frm_progmem_buttons, text="Load...")
        self.btn_load_prog.grid(row=0, column=0)
        self.btn_load_prog.bind("<ButtonRelease-1>", self.on_load_program)

        frm_progmem = Frame(self.frm)
        frm_progmem.grid(row=2, column=0)

        self.progmem_cells = []

        grid_size = int(sqrt(machine.PROGRAM_SIZE))

        for row in range(grid_size):
            for col in range(grid_size):
                ent = Entry(frm_progmem,
                            width=4,
                            font="TkFixedFont",
                            disabledforeground="#000")
                ent.grid(row=row, column=col)
                ent.bind("<FocusIn>", self.on_focus_entry)
                self.progmem_cells.append(ent)


        self.spacer(self.frm, 2, 1)

        Label(self.frm, text="Data Memory").grid(row=0, column=2)

        frm_datamem_buttons = Frame(self.frm)
        frm_datamem_buttons.grid(row=1, column=2)

        self.btn_load_data = Button(frm_datamem_buttons, text="Load...")
        self.btn_load_data.grid(row=0, column=0)
        self.btn_load_data.bind("<ButtonRelease-1>", self.on_load_data)

        frm_datamem = Frame(self.frm)
        frm_datamem.grid(row=2, column=2)

        self.datamem_cells = []

        grid_size = int(sqrt(machine.DATA_SIZE))

        for row in range(grid_size):
            for col in range(grid_size):
                ent = Entry(frm_datamem,
                            width=2,
                            font="TkFixedFont",
                            disabledforeground="#000")
                ent.grid(row=row, column=col)
                ent.bind("<FocusIn>", self.on_focus_entry)
                self.datamem_cells.append(ent)

        frm_registers = Frame(self.frm, pady=10)
        frm_registers.grid(row=3, column=0, columnspan=3)

        col_count = itertools.count()

        Label(frm_registers, text="PC =").grid(row=0, column=next(col_count))
        self.ent_pc = Entry(frm_registers, width=2, font="TkFixedFont",
                            disabledforeground="#000")
        self.ent_pc.grid(row=0, column=next(col_count))
        self.ent_pc.bind("<FocusIn>", self.on_focus_entry)

        self.spacer(frm_registers, 0, next(col_count))

        Label(frm_registers, text="A =").grid(row=0, column=next(col_count))
        self.ent_a = Entry(frm_registers, width=2, font="TkFixedFont",
                            disabledforeground="#000")
        self.ent_a.grid(row=0, column=next(col_count))
        self.ent_a.bind("<FocusIn>", self.on_focus_entry)

        self.spacer(frm_registers, 0, next(col_count))

        self.lbl_zeroflag = Label(frm_registers, text="ZERO")
        self.lbl_zeroflag.grid(row=0, column=next(col_count))

        self.lbl_signflag = Label(frm_registers, text="SIGN")
        self.lbl_signflag.grid(row=0, column=next(col_count))

        self.lbl_oddflag = Label(frm_registers, text="ODD")
        self.lbl_oddflag.grid(row=0, column=next(col_count))

        self.lbl_carryflag = Label(frm_registers, text="CARRY")
        self.lbl_carryflag.grid(row=0, column=next(col_count))

        self.spacer(frm_registers, 0, next(col_count))

        Label(frm_registers, text="P =").grid(row=0, column=next(col_count))
        self.ent_p = Entry(frm_registers, width=2, font="TkFixedFont",
                            disabledforeground="#000")
        self.ent_p.grid(row=0, column=next(col_count))
        self.ent_p.bind("<FocusIn>", self.on_focus_entry)

        col_count = itertools.count()

        frm_buttons = Frame(self.frm)
        frm_buttons.grid(row=4, column=0, columnspan=3)

        self.btn_start = Button(frm_buttons, text="Start")
        self.btn_start.grid(row=0, column=next(col_count))
        self.btn_start.bind("<ButtonRelease-1>", self.lock_ui)

        self.btn_stop = Button(frm_buttons, text="Stop")
        self.btn_stop.grid(row=0, column=next(col_count))
        self.btn_stop.bind("<ButtonRelease-1>", self.unlock_ui)
        self.btn_stop.configure(state=DISABLED)

        self.btn_step = Button(frm_buttons, text="Step")
        self.btn_step.grid(row=0, column=next(col_count))
        self.btn_step.bind("<ButtonRelease-1>", self.on_step_button)

        global ENTRY_FG_DEFAULT
        global ENTRY_BG_DEFAULT
        global ENTRY_DISABLED_BG_DEFAULT
        if ENTRY_FG_DEFAULT is None:
            assert(ENTRY_BG_DEFAULT is None)
            assert(ENTRY_DISABLED_BG_DEFAULT is None)
            ENTRY_FG_DEFAULT = self.ent_pc["fg"]
            ENTRY_BG_DEFAULT = self.ent_pc["bg"]
            ENTRY_DISABLED_BG_DEFAULT = self.ent_pc["disabledbackground"]

        self.machine_to_ui()


    def mark_entry_error(self, entry: Entry) -> None:
        entry.configure(fg="#fff")
        entry.configure(bg="#f00")


    def mark_entry_highlight(self, entry: Entry) -> None:
        entry.configure(fg="#000")
        entry.configure(disabledforeground="#000")
        entry.configure(bg="#ff4")
        entry.configure(disabledbackground="#ff4")


    def unmark_entry(self, entry: Entry) -> None:
        assert(ENTRY_FG_DEFAULT is not None)
        assert(ENTRY_BG_DEFAULT is not None)
        assert(ENTRY_DISABLED_BG_DEFAULT is not None)

        entry.configure(fg=ENTRY_FG_DEFAULT)
        entry.configure(disabledforeground=ENTRY_FG_DEFAULT)
        entry.configure(bg=ENTRY_BG_DEFAULT)
        entry.configure(disabledbackground=ENTRY_DISABLED_BG_DEFAULT)


    def flag_off(self, lbl_flag: Label) -> None:
        lbl_flag.configure(bg="#040")
        lbl_flag.configure(fg="#fff")


    def flag_on(self, lbl_flag: Label) -> None:
        lbl_flag.configure(bg="#0f0")
        lbl_flag.configure(fg="#000")


    def set_flag(self, lbl_flag: Label, state: bool) -> None:
        if state:
            self.flag_on(lbl_flag)
        else:
            self.flag_off(lbl_flag)


    def lock_ui(self, event: "Event[Button] | None") -> None:
        for i in range(machine.PROGRAM_SIZE):
            self.progmem_cells[i].configure(state=DISABLED)

        for i in range(machine.DATA_SIZE):
            self.datamem_cells[i].configure(state=DISABLED)

        self.ent_pc.configure(state=DISABLED)
        self.ent_a.configure(state=DISABLED)
        self.ent_p.configure(state=DISABLED)
        self.btn_load_prog.configure(state=DISABLED)
        self.btn_load_data.configure(state=DISABLED)
        self.btn_start.configure(state=DISABLED)
        # self.btn_step.configure(state=DISABLED)

        self.btn_stop.configure(state=NORMAL)

        self.is_locked = True


    def unlock_ui(self, event: "Event[Button] | None") -> None:
        for i in range(machine.PROGRAM_SIZE):
            self.progmem_cells[i].configure(state=NORMAL)

        for i in range(machine.DATA_SIZE):
            self.datamem_cells[i].configure(state=NORMAL)

        self.ent_pc.configure(state=NORMAL)
        self.ent_a.configure(state=NORMAL)
        self.ent_p.configure(state=NORMAL)
        self.btn_load_prog.configure(state=NORMAL)
        self.btn_load_data.configure(state=NORMAL)
        self.btn_start.configure(state=NORMAL)
        self.btn_step.configure(state=NORMAL)

        self.btn_stop.configure(state=DISABLED)

        self.is_locked = False


    def machine_to_ui(self) -> None:
        was_locked = self.is_locked

        if was_locked:
            self.unlock_ui(None)

        for i in range(machine.PROGRAM_SIZE):
            word = self.machine.program_memory[i]
            ent = self.progmem_cells[i]
            ent.delete(0, END)
            ent.insert(0, f"{word:04x}")
            if i == self.machine.program_counter:
                self.mark_entry_highlight(ent)
            else:
                self.unmark_entry(ent)

        for i in range(machine.DATA_SIZE):
            word = self.machine.data_memory[i]
            ent = self.datamem_cells[i]
            ent.delete(0, END)
            ent.insert(0, f"{word:02x}")
            if i == self.machine.register_p:
                self.mark_entry_highlight(ent)
            else:
                self.unmark_entry(ent)

        self.ent_pc.delete(0, END)
        self.ent_pc.insert(0, f"{self.machine.program_counter:02x}")

        self.ent_a.delete(0, END)
        self.ent_a.insert(0, f"{self.machine.register_a:02x}")

        self.ent_p.delete(0, END)
        self.ent_p.insert(0, f"{self.machine.register_p:02x}")

        self.set_flag(self.lbl_zeroflag, self.machine.zero_flag())
        self.set_flag(self.lbl_signflag, self.machine.sign_flag())
        self.set_flag(self.lbl_oddflag, self.machine.odd_flag())
        self.set_flag(self.lbl_carryflag, self.machine.carry_flag)

        if was_locked:
            self.lock_ui(None)


    def ui_to_machine(self) -> bool:
        success = True

        def read_entry(entry: Entry, max_value: int) -> int | None:
            nonlocal success

            contents = entry.get()
            try:
                word = int(contents, 16)

                if word > max_value:
                    raise ValueError("")

                return word
            except ValueError:
                success = False
                self.mark_entry_error(entry)
                return None

        for i in range(machine.PROGRAM_SIZE):
            if (word := read_entry(self.progmem_cells[i], machine.PROGRAM_MAX)) is not None:
                self.machine.store_program(i, word)

        for i in range(machine.DATA_SIZE):
            if (word := read_entry(self.datamem_cells[i], machine.DATA_MAX)) is not None:
                self.machine.store_data(i, word)

        if (pc := read_entry(self.ent_pc, machine.PROGRAM_SIZE)) is not None:
            self.machine.set_program_counter(pc)

        if (ra := read_entry(self.ent_a, machine.DATA_MAX)) is not None:
            self.machine.set_register_a(ra)

        if (rp := read_entry(self.ent_p, machine.DATA_SIZE)) is not None:
            self.machine.set_register_p(rp)

        if not success:
            messagebox.showerror("Wrong entry", "The entries made in the cells marked in red are not correct (hexadecimal numbers up to ff or ffff)")

        return success


    def load_from_file_into_entries(self, entries: List[Entry], width: int) -> None:
        filename = filedialog.askopenfilename()
        # When no file is selected, the dialog returns () on first use and "" thereafter.
        # Therefore, do *not* put a more explicit check here (also, don't tell mypy...)
        if filename:
            try:
                contents = open(filename).read()
                words = contents.replace("\n", " ").split()

                if len(words) > len(entries):
                    raise IndexError(f"The file is too long. It contains {len(words)} words, but the maximum is {len(entries)}.")

                for i in range(machine.PROGRAM_SIZE):
                    word = int(words[i], 16) if i < len(words) else 0

                    ent = entries[i]
                    ent.delete(0, END)
                    ent.insert(0, f"{word:0{width}x}")

            except Exception as e:
                messagebox.showerror("File format", f"Could not read the file.\n\nThe error was:\n{e}")


    def on_load_program(self, event: "Event[Button]") -> None:
        self.load_from_file_into_entries(self.progmem_cells, 4)

    def on_load_data(self, event: "Event[Button]") -> None:
        self.load_from_file_into_entries(self.datamem_cells, 2)


    def on_step_button(self, event: "Event[Button]") -> None:
        if self.ui_to_machine():
            self.machine.step()
            self.machine_to_ui()
        else:
            messagebox.showerror("Wrong entry", "The entries made in the cells marked in read are not correct (hexadecimal numbers up to ff or ffff)")


    def on_focus_entry(self, event: "Event[Entry]") -> None:
        self.unmark_entry(event.widget)



if __name__ == "__main__":
    root = Tk()

    ui = UI(root)

    root.mainloop()
