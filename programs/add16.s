	;; Add two 16-bit numbers given in memory locations 0,1 ("x") and
	;; 2,3 ("y"); write result into 4;5 ("z")

	.equ lowx 0
	.equ highx 1
	.equ lowy 2
	.equ highy 3
	.equ lowz 4
	.equ highz 5

	la lowx
	add lowy
	sta lowz

	lai 0
	jnc add2
	addi 1

	.l add2
	add highx
	add highy
	sta highz

	.l stop
	jmp stop
