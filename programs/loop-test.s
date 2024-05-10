	lai 0x1e 			; 30
loop:	subi 3
	jnz loop

	lai 0xff

stop:	jmp stop
