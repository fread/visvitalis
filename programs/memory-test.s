	lai 0x2a
	sta 0x00

	lai 0x01
	sta 0x01

	lai 0xff
	sta 0x02

	la 0x00
	nop
	la 0x01
	nop
	la 0x02

stop:	jmp stop
