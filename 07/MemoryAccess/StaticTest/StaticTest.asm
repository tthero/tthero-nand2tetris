// push constant 111
@111
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 333
@333
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 888
@888
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop static 8
@16
D=M
@8
D=A+D
@SP
A=M
M=D
@SP
AM=M-1
D=M
@SP
A=M+1
A=M
M=D
// pop static 3
@16
D=M
@3
D=A+D
@SP
A=M
M=D
@SP
AM=M-1
D=M
@SP
A=M+1
A=M
M=D
// pop static 1
@16
D=M
@1
D=A+D
@SP
A=M
M=D
@SP
AM=M-1
D=M
@SP
A=M+1
A=M
M=D
// push static 3
@16
D=M
@3
A=A+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push static 1
@16
D=M
@1
A=A+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// push static 8
@16
D=M
@8
A=A+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
