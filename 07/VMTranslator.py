"""
VM to HACK Translator Python Part 1
"""

import sys
import re

_PUSH_POP = ['push','pop']
_DOUBLE_OP = ['add','sub','and','or','gt','eq','lt']
_SINGLE_OP = ['not','neg']
_SEGMENTS = {'static':"16", 'constant':'','local':'LCL','argument':'ARG',
             'this':'THIS','that':'THAT','pointer':['THIS','THAT'],'temp':"5"}

# Counters
_jump_counter = 0

def VMParser(line, line_num):
    """
    VM Parser:
    Handles the input contents by parsing (or dissecting and analysing)
    each line of the VM code
    """
    
    result = []

    line = line.strip(" \n")
    # Comments handler
    if line.find("//") >= 0:
        line = line[:line.find("//")]

    if line:
        # Check for the syntax of the line
        # Remove all possible tabs 
        s = line.strip(' \t')
        while '\t' in s:
            s = s[:s.find('\t')] + s[s.find('\t')+1:]
        comm = []
        for i in s.split(" "):
            if i:
                comm.append(i)
        
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

        result = comm

    return result


def ASMCodeWriter(comms):
    """
    ASM Code Writer:
    Outputs appropriate assembly codes based on parsed inputs from
    the Parser
    """

    result = ""

    # Debug: print the VM code in comment form:
    result += '// ' + ' '.join(comms) + '\n'

    def push_pop(comms):
        nonlocal result

        segment, val = comms[1:]
        # PUSH
        if comms[0] == "push":
            # Determining the segment
            if segment == "constant":
                result += '\n'.join((
                    "@" + val,
                    "D=A"
                ))
            elif segment == "pointer":
                result += '\n'.join((
                    "@" + _SEGMENTS[segment][int(val)],
                    "D=M"
                ))
            elif segment == "temp":
                result += '\n'.join((
                    "@" + _SEGMENTS[segment],
                    "D=A",
                    "@" + val,
                    "A=A+D",
                    "D=M"
                ))
            else:
                result += '\n'.join((
                    "@" + _SEGMENTS[segment],
                    "D=M",
                    "@" + val,
                    "A=A+D",
                    "D=M"
                ))
            result += '\n'
        
            # Dealing with stack pointer (SP)
            result += '\n'.join((
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ))
        # POP
        else:
            # Determining the segment
            if segment == "pointer":
                result += '\n'.join((
                    "@" + _SEGMENTS[segment][int(val)],
                    "D=A"
                ))
            elif segment == "temp":
                result += '\n'.join((
                    "@" + _SEGMENTS[segment],
                    "D=A",
                    "@" + val,
                    "D=A+D"
                ))
            else:
                result += '\n'.join((
                    "@" + _SEGMENTS[segment],
                    "D=M",
                    "@" + val,
                    "D=A+D"
                ))
            result += '\n'
            
            # Dealing with stack pointer (SP)
            result += '\n'.join((
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "AM=M-1",
                "D=M",
                "@SP",
                "A=M+1",
                "A=M",
                "M=D"
            ))
    
    def arithmetics(comms):
        nonlocal result

        if comms[0] in _DOUBLE_OP:
            # Beginning of common section
            result += '\n'.join((
                "@SP",
                "AM=M-1",
                "D=M",
                "A=A-1"
            ))
            result += '\n'

            # Add, sub, and, or, gt, eq, lt
            if comms[0] == "add":
                result += "M=M+D"
            elif comms[0] == "sub":
                result += "M=M-D"
            elif comms[0] == "and":
                result += "M=M&D"
            elif comms[0] == "or":
                result += "M=M|D"
            elif comms[0] in ["gt", "eq", "lt"]:
                global _jump_counter

                result += '\n'.join((
                    "D=M-D",
                    "M=-1",
                    "@TRUE" + str(_jump_counter),
                    "D;JGT" if comms[0] == "gt" else (
                        "D;JEQ" if comms[0] == "eq" else "D;JLT"
                    ),
                    "@SP",
                    "A=M-1",
                    "M=0",
                    "(TRUE" + str(_jump_counter) + ")"
                ))

                _jump_counter += 1
        else:
            result += '\n'.join((
                "@SP",
                "A=M-1",
                "M=!M",
                "M=M+1" if comms[0] == "neg" else ""
            ))

    if comms[0] in _PUSH_POP:
        push_pop(comms)
    elif comms[0] in _DOUBLE_OP + _SINGLE_OP:
        arithmetics(comms)
    
    result += '\n'
    
    return result

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
        # VM code parser
        for line in vm_file:
            r = VMParser(line, line_num)
            if r:
                res.append(r)
            line_num += 1

        # Assembly code writer
        for line in res:
            asm_file.write(ASMCodeWriter(line))
        
        print("VM Translation succeeded.")
    except SyntaxError as err:
        print("Syntax error on", err)
        print("VM Translation failed.")
    finally:
        vm_file.close()
        asm_file.close()

if __name__ == "__main__":
    VMTranslator()