	;; Find maximum value in a list
	;; list start in address 0, list end in address 1

	.equ list_start 0
	.equ list_end 1

	.equ result 0xff

	;; local variables
	.equ cursor 2
	.equ max 3

	la list_start
	sta cursor
	lai 0
	sta max

	.l loop
	la cursor
	sub list_end
	jge end
	lp cursor
	la max
	subp
	jl newmax
	jmp inc

	.l newmax
	lp cursor
	lap
	sta max

	.l inc
	la cursor
	addi 1
	sta cursor
	jmp loop

	.l end
	la max
	sta result

	.l stop
	jmp stop
