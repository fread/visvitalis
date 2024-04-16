	;; Insertion sort
	;;
	;; Code taken from Wikipedia (https://en.wikipedia.org/wiki/Insertion_sort):
	;; i ← 1
	;; while i < length(A)
	;;     x ← A[i]
	;;     j ← i
	;;     while j > 0 and A[j-1] > x
	;;         A[j] ← A[j-1]
	;;         j ← j - 1
	;;     end while
	;;     A[j] ← x
	;;     i ← i + 1
	;; end while
	;;
	;; However, our i and j are pointers into the array, hence i
	;; starts at list_start + 1, and we compare to
	;; list_start/list_end instead of 0/length(A).
	;;
	;; Also we check for A[j-1] >= x in the inner loop, which
	;; happens to be easier for the flags to handle.
	;;
	;; start of list at address 0
	;; end of list at address 1

	.equ list_start 0
	.equ list_end 1

	;; local variables
	.equ i 2
	.equ j 3
	.equ x 4
	.equ tmp 5

	la list_start
	addi 1
	sta i

	.l outer_loop
	la i
	sub list_end
	jge stop

	lp i
	lap
	sta x

	la i
	sta j

	.l inner_loop
	la j
	sub list_start
	jz inner_end
	la j
	subi 1
	a2p
	lap
	sub x
	jl inner_end

	la j
	subi 1
	a2p
	lap
	lp j
	stap

	la j
	subi 1
	sta j

	jmp inner_loop

	.l inner_end

	la x
	lp j
	stap

	la i
	addi 1
	sta i

	jmp outer_loop

	.l stop
	jmp stop
