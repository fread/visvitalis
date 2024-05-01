	lai 0x1e 			; 30
.l loop
	subi 3
	jnz loop

	lai 0xff

.l stop
	jmp stop
