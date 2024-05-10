	;; Multiplication
	;;
	;; First argument at address 0,
	;; second argument at address 1,
	;; result at address 2

	.equ x_in 0
	.equ y_in 1
	.equ r_out 2

	.equ x 0x10
	.equ y 0x11
	.equ acc 0x12

	;; Move inputs to local variables so as not to clobber them
	la x_in
	sta x
	la y_in
	sta y

	lai 0
	sta acc

loop:	la x
	jz end
	jev noadd
	la y
	add acc
	sta acc
noadd:	la x
	shr
	sta x
	la y
	add y
	sta y
	jmp loop

end:	la acc
	sta r_out

stop:	jmp stop
