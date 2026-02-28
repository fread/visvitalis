.equ sp 255
.equ fp 254
.equ ret 253
.equ noret 252
.equ temp 251
.equ dest 249


; fix registers
lai 240
sta sp
sta fp
;lai 0
;sta ret

jmp main


.pos 0x10
; push a to stack
push:
  sta temp
  la sp
  addi -1
  sta sp
  a2p
  la temp
  stap
  lp noret
  jp

.pos 0x20
; pop a from stack
pop:
  la sp
  addi 1
  sta sp
  a2p
  lap
  lp noret
  jp

.pos 0x30
call:
  ; all parameters already on stack
  ; return address already in dest
  ; fp points to upper params
  ; sp points to lower params
  lai call_push_fp
  sta noret
  la fp
  jmp push
  call_push_fp:
  lai call_push_sp
  sta noret
  la sp
  jmp push
  call_push_sp:
  lai call_push_ret
  sta noret
  la ret
  jmp push
  call_push_ret:
  la sp
  sta fp
  lp dest
  jp

.pos 0x50
return:
  ; result currently pointed to by sp
  ; result in accu afterwards
  la sp
  addi 4
  sta sp
  la sp
  addi -3 ; return
  a2p
  lap
  sta ret
  la sp
  addi -1 ; fp
  a2p
  lap
  sta fp
  la sp
  addi -4 ; result
  a2p
  lap
  lp ret
  jp


.pos 0x70
fib:
  ; load param (currently three above fp given the pushes)
  la fp
  addi 3
  a2p
  lap
  addi -2 ; fix recursion termination check
  js recursion_stop
  ; substract 1 of val and call fib once
  addi 2 ; revert fix, do not merge with next line
  addi -1
  ; TODO, currently fallthrough on purpose
  sta temp
  lai fib_call_push_first
  sta noret
  la temp
  jmp push
  fib_call_push_first:
  lai fib_call_first
  sta ret
  lai fib
  sta dest
  jmp call
  fib_call_first:
  lp sp
  stap
;  lai fib_push_first_result
;  sta noret
;  la temp
;  jmp push
  la fp
  addi 3
  a2p
  lap ; param again
  addi -2
  sta temp
  lai fib_call_push_second
  sta noret
  la temp
  jmp push
  fib_call_push_second:
  lai fib_call_second
  sta ret
  lai fib
  sta dest
  jmp call
  fib_call_second:
  lp sp
  stap
;  sta temp
;  lai fib_push_second_result
;  sta noret
;  la temp
;  jmp push
;  fib_push_second_result:

  la sp
  addi 1
  a2p
  lap
  sta temp
  lp sp
  lap
  add temp ; THIS ACTUALLY ADDS!!!!
  sta temp
  la fp
  addi -1
  a2p
  la temp
  stap
  la sp
  addi 1
  sta sp
  jmp return



  recursion_stop:
  lai recusion_stop_after_push
  sta noret
  lai 1
  jmp push
  recusion_stop_after_push:
  jmp return

  recursion_different:
  lai recursion_different_after_push
  sta noret
  lai 3
  jmp push
  recursion_different_after_push:
  jmp return

.pos 0xc0
main:
  ; ret = main_after_call
  ; param = 0
  lai main_after_push_param
  sta noret
  lai 4
  jmp push
  main_after_push_param:
  ; dest = fib
  lai fib
  sta dest
  lai main_after_call
  sta ret
  jmp call
  main_after_call:
  jmp main_after_call ; infinite loop to show result

  

