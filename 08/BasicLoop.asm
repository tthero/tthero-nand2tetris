// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// if-goto FDFD
@SP
AM=M-1
D=M
@$FDFD
D;JGT
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// label FDFD
($FDFD)
// push constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
// label EF
($EF)
// goto EF
@$EF
0;JMP
