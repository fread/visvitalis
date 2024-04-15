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
	la list_end
	sub cursor
	js end
	lp cursor
	lap
	sub max
	jns newmax
	la cursor
	addi 1
	sta cursor

	.l newmax
	lp cursor
	lap
	sta max
	jmp loop

	.l end
	la max
	sta result
