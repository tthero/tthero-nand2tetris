// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)


// Multiplication is addition by n times
// In this case, RAM[R2] is added by RAM[R0] for RAM[R1] times

// RAM[R2] can be directly used as result
// Pseudocode:
// result = 0
// x = RAM[R0]
// n = RAM[R1]
// i = 0
// LOOP:
//     if (n - i) == 0:
//         goto END
//     result = result + x
//     i = i + 1
//     goto LOOP
// END:
//     RAM[R2] = result

    @R2
    M = 0   // RAM[R2] = 0
    @R0
    D = M
    @x
    M = D   // x = RAM[R0]
    @R1
    D = M
    @n
    M = D   // n = RAM[R1]
    @i
    M = 0   // i = 0
(LOOP)      // for(i=0; n-i>0; i++)
    @i
    D = M   // current i
    @n
    D = M - D   // n = n - i
    @END
    D;JEQ   // if (n == 0): goto END
    @x
    D = M
    @R2
    M = M + D   // RAM[R2] += x
    @i
    M = M + 1   // i += 1
    @LOOP
    0;JMP   // goto LOOP
(END)
    @END
    0;JMP   // EXIT
