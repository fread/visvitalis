	;; Computes fibonacci numbers and puts the in the P register.
	;; Attach LEDs to P's output to see them.

	.equ f_2 0
	.equ f_1 1
	.equ f_0 2

restart: lai 0
	sta f_2
	lai 1
	sta f_1

loop:	la f_2
	add f_1
	sta f_0

	jc restart

	a2p

	la f_1
	sta f_2
	la f_0
	sta f_1

	jmp loop
