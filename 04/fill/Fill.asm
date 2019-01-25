// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
// Pseudocode:
// while(true) {
//     for(i=16384; i<24576; i++) {
//         if(RAM[24576] > 0) {
//             RAM[i] = -1;
//         }
//         else {
//             RAM[i] = 0;
//         }
//     }
// }
(LOOP)
    @SCREEN
    D = A
    @i
    M = D   // i = SCREEN
(SCRLOOP)
    @i
    D = M
    @KBD
    D = A - D   // KBD - i
    @LOOP
    D;JEQ   // if (KBD - i == 0): goto LOOP
    @KBD
    D = M
    @KEYPRESS
    D;JGT   // if (RAM[KBD] > 0): goto KEYPRESS
    @i
    A = M
    M = 0   // RAM[i] = 0
    @ENDKEY
    0;JMP   // goto ENDKEY
(KEYPRESS)
    @i
    A = M
    M = -1  // RAM[i] = -1
(ENDKEY)
    @i
    M = M + 1   // i = i + 1
    @SCRLOOP
    0;JMP   // goto SCRLOOP


