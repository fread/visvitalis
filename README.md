# vis vitalis - A very simple modular relay processor

This project contains plans for [PCB modules](/new-parts/) to build a relay processor, complete with [assembler](/assembler/) and [emulator](/emulator/).
While the actual processor is made out of relays (and the occasional diode), memory is emulated by ESP-based boards.
Their [firmware](/mem-esp-firmware/) also provides for loading programs and monitoring memory contents via a USB-TTY connection.

## Why though?

Processors are, fundamentally, not *that* complicated.
At any rate, you can build one out of much less than the billions of transistors required for a desktop CPU.
And it's a worthwhile endeavour, too, being actually able to understand a whole processor, albeit a very simple one.

### But why the name?

*vis vitalis*, meaning “force of life”, was a concept in early chemistry.
When it was first discovered that everything is made up of the same elements, people would not accept that this also applies to living beings.
Thus, they postulated the *vis vitalis* as a peculiar element present in everything living, unable to be replicated outside of biological processes.

Today, of course, we know that there is no fundamental difference at all between Turing-complete electronics and any others.

## The modules

Individually, each module performs a simple task – the trick is in how to put them together, for which see below.

In the module description, we use the usual tri-state convention for signal levels: `0` and `1` are signals actively driven low or high respectively, and `Z` is high-impedance, i. e. an unconnected signal.
In some cases, `0` and `Z` are interchangable but most modules require actively driven `0` signals at their inputs to work.

The modules are connected with 10-way ribbon cables carrying eight bits of data as well as 12V positive supply and ground.
Thus, not every module needs its own power supply connection.
Only modules which either draw a lot of current, or which require a stable supply, have a separate power connection.

### 8mux

An eight-bit multiplexer.
If the *select* input is `0` or `Z`, input *in 0* is connected to *out*.
If *select* is `1`, *in 1* is connected to *out*.

The multiplexer passes through signals between the connected terminals in both directions, though from a logical point of view the signals will almost always “flow” from *in* to *out*.

### add

Outputs the sum of *A in*, *B in*, and *carry in* on *A+B out* and *carry out*.
Note that the A operand and the carry bit is also required inverted (*A̅ in* and *c̅a̅r̅r̅y̅ in*).
All inputs must be `0` or `1`, and all outputs will be `0` or `1`.

For normal addition, set *carry in* to `0` and *c̅a̅r̅r̅y̅ in* to `1`.
If you want to subtract rather than add, invert the B and carry inputs (i. e. *carry in* = `1`, *c̅a̅r̅r̅y̅ in* = `0`).

#### Acknowledgement

This design of adder goes back to Konrad Zuse himself, I was made aware of it by the documentation of the
[RelaySBC](https://relaysbc.sourceforge.net/circuits.html) and this
[collection of relay circuits](https://tams.informatik.uni-hamburg.de/applets/hades/webdemos/05-switched/20-relays/zuseadd.html).
Its advantage is that there is no cascading from one relay to another.
All the relays switch in parallel and only steer the inverted and non-inverted signals around.

### clk

The clock generator.
With the values indicated in the schematic, and not populating R3–R6 (again, as indicated), the clock runs at a bit less than 1 Hz.
Populating R3 and R4 with a value of 1 to 15 kΩ slows down the clock, and populating R5 and R6 speeds it up.

#### Acknowledgement

This design was found with some shrewd (or so I'd like to think) internet research.
It originates from https://imgur.com/iKWSAM1.

### decode

In some sense, the instruction decoder is the heart of the processor, though this one mainly distributes the bits of the incoming instruction (*insn in*) to the control outputs (*control out*).

Other than that, it only performs a small assortment of simple logic:
- Relay K1 produces the clock pulses for the `p enable` and `a enable` outputs (to write the the corresponding registers)
- Relays K2, K3, and K5 implement a one-bit register for the carry flag to save the result of the last addition or subtraction.
  The carry register is written whenever the *adder* control signal is `1`.
- The other relays evaluate jump instructions.
  If the current instruction is a jump, they compare the current state of the flags (including the carry register) with the condition called for by the jump.
  They then output the decision to jump or to continue with the next instruction on *pc src out*.

Flag inputs must be `0` or `1`.
Instruction bit 5 must be `0` or `1`. 
The other bits may use `Z` instead of `0`, in which case the corresponding control output is also `Z`.

### disp

This module may be inserted into any data connection to view its current state.
It displays `Z` as `0`.

### flags

This module examines its input for three conditions, and outputs them:
- *odd*: The lowest bit of the input is set
- *sign*: The highest bit of the input is set
- *zero*: The input is zero

Inputs to this module may be `Z`, but then the *odd* and *sign* outputs will also be `Z`, which will not work with the *decode* module.

### inc

Increments the input *A in* and outputs the result on *A+1 out*.
Incrementers may be chained using the *carry in* and *carry out* connections.
The carry input of the first incrementer in a chain (or a standalone incrementer) must be tied to `1`.
This may be done by closing the solder bridge JP1.
In this case, *carry in* should be left unconnected.

All inputs must be `0` or `1`, and all outputs will be `0` or `1`.

### inv

The output *A̅ out* is the bitwise complement of *A in*.
Input values `0` and `Z` map to `1`, and `1` maps to `0`.

### jnc

Just a junction box.

### mem-esp

This module simulates both the program and the data memory.
From the processor's perspective, the program memory is an 8×16 bit ROM, and the data memory is an 8×8 bit RAM.
In addition, it has a USB-TTY connection, so that the memories may be loaded and monitored from a host computer.
Refer to the [documentation in the firmware directory](/mem-esp-firmware/README.md) for how to operate the TTY console.

The *addr in* input takes the address of the data to be read or written.
The *data1 i/o* connection operates either as an input or as an output, depending on the signal at the *w/r̅* input.
*data2 out* is always an output.

If the module is used as ROM, the input side of input no. 1 may not be populated (i. e., leaving out U3, U4, and R1–R16).
If the module is used as an 8×8 bit memory, the second output may not be populated (i. e., leaving out J8, U9, C9–C13).
In this case, the solder bridge JP4 needs to be closed in order to complete the SPI chain.

#### Operation

If the *w/r̅* input is `0` or `Z`, the module operates in read mode.
The output drivers at the *data1 i/o* and (if populated) *data2 out* connections will be active, and output the data found in memory at the address present at the *addr in* input.
The output changes asynchronously with the clock signal, but after a short delay to smooth out any glitches while switching.

If the *w/r̅* input is `1`, the module operates in write mode.
The output drivers are not active, and *data1 i/o* operates as an input.
At the clock's rising edge, the firmware starts sampling the state of *data1 i/o*.
At the clock's falling edge, it updated the memory contents.
For each bit, the most majority value seen in the samples is used, again to smooth out glitches and to account for propagation delays.
`Z` inputs are taken as `0`.

The switch between read and write mode occurs asynchronously.
As soon as the signal at the *w/r̅* input changes, the drivers are activated or deactivated.
Make sure that no signals are sent to the memory module in read mode.
This will lead to an overcurrent condition, and may damage parts.

### nor

This module implements a NOR gate.
For each bit of *A in* and *B in*, the corresponding output bit is `0` if any input is `1`, otherwise (both inputs `0` or `Z`) it is `1`.

### reg

This module is an eight-bit register.
While the *clock* input is `1`, it samples the value of the *in* input.
On the falling edge of the *clock* input (either to `0` or to `Z`), the sampled data is transferred to the buffer stage, and the outputs *out* and *o̅u̅t̅* (inverted) are updated.

The *override* input may be used to asnychronously set bits.
In normal operation, all bits should be `Z`.
Setting them to `0` or `1` causes the corresponding output to change immediately.
Since there are no resistors in the override path, bits should be set one or a few at a time.

### shr

This module shifts its input to the right by one bit.
It contains no logic.

### switch

This module may be used to provide inputs to a partial setup of other modules for testing purposes, or to override a register.
If it is used for overriding a register, it needs switches with a stable center position in order to provide `Z` outputs.

## The whole thing

## Errata

- The LEDs specified on the *disp* and *switch* modules are way too bright in this configuration, even when increasing the series resistors to 2.2 kΩ.
- On the *reg* module, you may want to use larger input resistors (R9–R16) to lower the peak current at the beginning of the write cycle (clock rising edge).
- You may want to exchange the pin headers for control signals for sockets. Then you can use a simple wire in a pinch instead of requiring a jumper with sockets on either end.
