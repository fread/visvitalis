# Instruktionen

## Berechnen

In der folgenden Liste bedeutet:

* **A** der Inhalt des Akku-Registers
* **P** der Inhalt des Pointer-Registers
* **M[a]** der Inhalt des Speichers an der Adresse **a**

| Insn     | Code              | Beschreibung                                               |
|----------|-------------------|------------------------------------------------------------|
| `a2p`    | P = A             | Kopiere Akku in Pointer                                    |
| `add x`  | A = A + M[x]      | Addiere Variable zu Akku                                   |
| `addi x` | A = A + x         | Addiere Wert zu Akku                                       |
| `addp`   | A = A + M[P]      | Addiere Pointer-Ziel zu Akku                               |
| `clm x`  | M[x] = 0          | Setze Variable auf 0                                       |
| `clmp`   | M[P] = 0          | Setze Pointer auf 0                                        |
| `la x`   | A = M[x]          | Lade Variable in Akku                                      |
| `lai x`  | A = x             | Lade Wert in Akku                                          |
| `lap`    | A = M[P]          | Lade Pointer-Ziel in Akku                                  |
| `lp x`   | P = M[x]          | Lade Variable in Pointer                                   |
| `lpi x`  | P = x             | Lade Wert in Pointer                                       |
| `lpp`    | P = M[P]          | Lade Pointer-Ziel in Pointer                               |
| `nor x`  | A = A NOR M[x]    | Berechne NOR zwischen Akku und Variable                    |
| `nori x` | A = A NOR x       | Berechne NOR zwischen Akku und Wert                        |
| `norp`   | A = A NOR M[P]    | Berechne NOR zwischen Akku und Pointer-Ziel                |
| `nop`    |                   | Tu nichts                                                  |
| `shr`    | A = A >> 1        | Schiebe Akku ein Bit nach rechts                           |
| `shrs x` | M[x] = A = A >> 1 | Schiebe Akku ein Bit nach rechts und speichere in Variable |
| `sta x`  | M[x] = A          | Speichere Akku in Variable                                 |
| `stap`   | M[P] = A          | Speichere Akku in Pointer-Ziel                             |
| `stip x` | M[P] = x          | Speichere Wert in Pointer-Ziel                             |
| `sub x`  | A = A - M[x]      | Subtrahiere Variable von Akku                              |
| `subi x` | A = A - x         | Subtrahiere Wert von Akku                                  |
| `subp`   | A = A - M[P]      | Subtrahiere Pointer-Ziel von Akku                          |

## Springen

| Insn.   | Beschreibung                             |
|---------|------------------------------------------|
| `jmp x` | Springe zu x                             |
| `jc x`  | Springe zu x wenn Carry gesetzt          |
| `jge x` | Springe zu x wenn Carry gesetzt          |
| `jnc x` | Springe zu x wenn Carry nicht gesetzt    |
| `jl x`  | Springe zu x wenn Carry nicht gesetzt    |
| `js x`  | Springe zu x wenn Akku negativ ist       |
| `jns x` | Springe zu x wenn Akku nicht negativ ist |
| `jz x`  | Springe zu x wenn Akku 0 ist             |
| `jnz x` | Springe zu x wenn Akku nicht 0 ist       |
| `jev x` | Springe zu x wenn Akku gerade ist        |
| `jod x` | Springe zu x wenn Akku ungerade ist      |
| `jp`    | Springe zu P                             |
| `jcp`   | Springe zu P wenn Carry gesetzt          |
| `jncp`  | Springe zu P wenn Carry nicht gesetzt    |
| `jsp`   | Springe zu P wenn Akku negativ ist       |
| `jnsp`  | Springe zu P wenn Akku nicht negativ ist |
| `jzp`   | Springe zu P wenn Akku 0 ist             |
| `jnzp`  | Springe zu P wenn Akku nicht 0 ist       |
| `jevp`  | Springe zu P wenn Akku gerade ist        |
| `jodp`  | Springe zu P wenn Akku ungerade ist      |

## Illegale Instruktionen

Opcodes dürfen selbst zusammengebaut werden. Manche tun sinnvolle Dinge.

| Bit | wenn 0                  | wenn 1                         | Bemerkungen                          |
|-----|-------------------------|--------------------------------|--------------------------------------|
| 7   |                         | Ergebnis in Speicher schreiben | wenn Bits (7, 6, 5) == 000: Sprung   |
| 5   |                         | Ergebnis in P schreiben        |                                      |
| 5   |                         | Ergebnis in A schreiben        |                                      |
| 4   | Ergebnis von Operand/A  | Ergebnis von ALU               |                                      |
| 3   | Ergebnis von Operand    | Ergebnis von A                 | wenn Bit 4 == 0                      |
| 3   | ALU Shift/Add           | ALU NOR/Subtract               | wenn Bit 4 == 1                      |
| 2   | ALU Shift/NOR           | ALU Add/Subtract               | 00: Shift, 01: Add, 10: NOR, 11: Sub |
| 1   | Operand aus Speicher    | Operand aus Instruktion        | "Immediate"                          |
| 0   | Adresse aus Instruktion | Adresse aus P                  | "indirekt"                           |

z. B. `0x5a 1`: P = A - 1

Bei Sprüngen gibt es keine illegalen Instruktionen, alle möglichen Instruktionen haben Mnemonics.

# Programmieren

## `uint8_t x;`
Adressen für Variablen mit `.equ` vergeben.
```asm
.equ x 23
```

## `x = 5;`
```asm
lai 5
sta x
```

## `x = y;`
```asm
la y
sta x
```

## `a = b + c`
```asm
la a
add b
sta c
```

## `if (x >= y) goto z;`
Für `jc` Und `jnc` gibt es die suggestiv benannten alternativen Mnemonics `jge` und `jl`:
```asm
la x
sub y
jge z
```

## `if (x < y) goto z;`
```asm
la x
sub y
jl z
  ```

## `while (x != 0) { xxx } yyy`
```asm
loop:
  la x
  jz end
  xxx
  jmp loop
end:
  yyy
  ...
```

## `x = a[i]`
```asm
la a
add i
a2p
lp
sta x
```

## `a[i] = x`
```asm
la a
add i
a2p
la x
stp
```

# Projektideen

* Lauflicht (hin und her?)
* Fibonacci
* Maximum suchen
* {mem,str}{cpy,chr,mem,str,...}
* Array umdrehen
* Multiplikation
* Binäre Suche
* Illegale Instruktionen ausprobieren
* Division
* Fizzbuzz
* Call/Return
* RPN-Evaluator
