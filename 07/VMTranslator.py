"""
VM to HACK Translator Python
"""
import sys
import re

_PUSH_POP = ['push','pop']
_DOUBLE_OP = ['add','sub','and','or','gt','eq','lt']
_SINGLE_OP = ['not','neg']
_SEGMENTS = {'static':16,'constant':'','local':'LCL','argument':'ARG',
             'this':'THIS','that':'THAT','pointer':['THIS','THAT'],'temp':5}

def VMParser(line, line_num):
    """
    VM Parser:
    Handles the input contents by parsing (or dissecting and analysing)
    each line of the VM code
    """
    
    result = []

    line = line.strip(" \n")
    # (1) Comments handler
    if line.find("//") >= 0:
        line = line[:line.find("//")]

    if line:
        # (3) Check for the syntax of the line
        comm = line.split(' ')
        try:
            if comm[0] in _PUSH_POP:
                if len(comm) < 3:
                    raise SyntaxError("Line " + str(line_num) + " - " + "Too few arguments in " + comm[0] + ".")
                elif len(comm) > 3:
                    raise SyntaxError("Line " + str(line_num) + " - " + "Too many arguments in " + comm[0] + ".")

                if comm[0] == 'pop' and comm[1] == 'constant':
                    raise SyntaxError("Line " + str(line_num) + " - " + "Constant cannot be used in pop.")
                    
                if comm[1] in _SEGMENTS:
                    if not comm[2].isdigit() and int(comm[2]) < 0:
                        raise SyntaxError("Line " + str(line_num) + " - " + comm[0].capitalize() + " only allows non-negative integers.")
                    elif not comm[2]:
                        raise SyntaxError("Line " + str(line_num) + " - " + "Missing non-negative integers in " + comm[0] + ".")
                    elif comm[1] == 'pointer' and int(comm[2]) >= 2:
                        raise SyntaxError("Line " + str(line_num) + " - " + comm[1] + " only allows 0/1 in " + comm[0] + ".")
                else:
                    raise SyntaxError("Line " + str(line_num) + " - " + "Unrecognised segment.")

            elif comm[0] in _DOUBLE_OP + _SINGLE_OP:
                if len(comm) > 1:
                    raise SyntaxError("Line " + str(line_num) + " - " + "Too many arguments.")

            else:
                raise SyntaxError("Line " + str(line_num) + " - " + "Unrecognised command.")
        except SyntaxError as err:
            print("Syntax error on", err)
            print("VM Translation failed.")
        except Exception:
            raise SyntaxError("Line " + str(line_num) + " - " + "Unrecognised segment.")

        result = comm

    return result


def ASMCodeWriter(comms):
    """
    ASM Code Writer:
    Outputs appropriate assembly codes based on parsed inputs from
    the Parser
    """

    """
    push segment i
    === segment ===
    @segment
    D=M
    @i  // constant
    A=A+D
    D=M
    === push ===
    @SP
    A=M
    M=D
    @SP
    M=M+1
    ============

    pop segment i
    === segment ===
    @segment
    D=M
    @i // constant
    D=A+D
    === pop ===
    @SP
    A=M
    M=D
    @SP
    AM=M-1
    D=M
    @SP
    A=M+1   // RAM[0]+1 = (SP-1)+1
    A=M     // RAM[RAM[0]+1] = segment+i
    M=D     // RAM[segment+i]
    ===========

    === add/sub/and/or ===
    @SP
    AM=M-1
    D=M
    A=A-1
    M=M+D or M=M-D or M=M&D or M=M|D

    === not/neg ===
    @SP
    A=M-1
    M=!M
    M=M+1 (for neg only)

    === lt/gt/eq ===
    @SP
    AM=M-1
    D=M
    A=A-1
    D=M-D
    M=-1
    @TRUE
    D;JLT / D;JGT / D;JEQ
    @SP
    A=M-1
    M=0
    (TRUE)

    """

    def push_pop():
        # Segment and constant
        s = _SEGMENTS[comms[1]]
        
        # Common parts (part 1)
        
        @segment
        D=M
        @i  // constant
        A=A+D
        D=M

    
    if comms[0] in _PUSH_POP:
        push_pop(comms)
    elif comms[0] in 
    

def VMTranslator():
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Error: File name is expected.")
        return 1

    pattern = re.compile(r"^[^.]+$|^.+\.vm$")
    s = re.findall(pattern, filename)
    
    if len(s) == 0:
        print("Error: Either file is not found or file name is expected.")
        return 2

    s = s[0].rsplit('.', maxsplit=1)[0]

    read_ext = ".vm"
    result_ext = ".asm"
    try:
        vm_file = open(s + read_ext, "r")
        asm_file = open(s + result_ext, "w")
    except FileNotFoundError:
        print("Error: File is not found.")
        return 3

    res = []
    line_num = 1
    try:
        # (1) Input handler: Parser
        pass
        # (2) Output handler: Code Writer
        pass

        # VM code parser
        for line in vm_file:
            r = VMParser(line, line_num)
            if r:
                res.append(r)
            line_num += 1

        # Assembly code writer
        # for line in res:
        #     asm_file.write(ASMCodeWriter(line))
        
        print("VM Translation succeeded.")

    finally:
        vm_file.close()
        asm_file.close()

if __name__ == "__main__":
    VMTranslator()