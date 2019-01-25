"""
HACK Assembler Python
"""
import sys
import re

# Global constants
_DESTS = {"A":"100", "D":"010", "M":"001", "AD":"110", "AM":"101",
          "MD":"011", "AMD":"111"}
_JUMPS = {"JGT":"001", "JEQ":"010", "JGE":"011", "JLT":"100",
          "JLE":"110", "JNE":"101", "JMP":"111"}
_OPS = ["!","-","+","&","|"]
_ALU_COMPS = {"0":"101010", "1":"111111", "D":"001100", 
              "A":"110000", "!D":"001101", "!A":"110001", 
              "D+1":"011111", "A+1":"110111", "D+A":"000010", 
              "-1":"111010", "-D":"001111", "-A":"110011", 
              "D-1":"001110", "A-1":"110010", "D-A":"010011", 
              "A-D":"000111", "D&A":"000000", "D|A":"010101"}

# Globals to be written:
_act_lines = 0
_label_con = {}
_variables = {}

def HackTranslate(line):
    """
    Hack translator:
    // = Comment, no need to translate
    \\t = Tabline
    A-instruction:
        Format: 0000000000000000
        Starts with 0
        (1) Non-negative integer constant
        (2) Symbol (Name with ASCII characters(?) or from 
            built-ins) translated to memory address
        (3) Instruction number to jump to
    C-instruction:
        Format: 111accccccdddjjj
        Starts with 111
        (1) a with cccccc 
    """
    global _act_lines
    global _label_con
    global _variables
    result = ""
    MAX_DIGIT = START_RAM = 16
    BUILT_IN = {"R0":0, "R1":1, "R2":2, "R3":3, "R4":4, "R5":5, 
                "R6":6, "R7":7, "R8":8, "R9":9, "R10":10, 
                "R11":11, "R12":12, "R13":13, "R14":14, "R15":15, 
                "SP":0, "LCL":1, "ARG":2, "THIS":3, "THAT":4, 
                "SCREEN":16384, "KBD":24576}

    if line:
        # (1) A-instruction
        if line[0] == "@":
            if line[1:] in BUILT_IN:
                # Convert decimal to binary
                result += '{:0b}'.format(BUILT_IN[line[1:]])
            elif line[1:].isdigit():
                # Whole string is made up of digits
                result += '{:0b}'.format(int(line[1:]))
            else:
                # Referring to label jumping
                if line[1:] in _label_con:
                    result += '{:0b}'.format(_label_con[line[1:]])
                else:
                    if line[1:] not in _variables:
                        _variables[line[1:]] = START_RAM + len(_variables)
                    result += '{:0b}'.format(_variables[line[1:]])

            result = '0'*(MAX_DIGIT - len(result)) + result

        # (2) C-instruction
        # 111 a cccccc ddd jjj
        else:
            result += '111'
            if len(line.split("=")) > 1:
                s = line.split("=")
                # "=": dest = comp
                # For comp
                result += ('1' if "M" in s[1] else '0')
                ALU = s[1].replace("M", "A")
                # "+", "&", "|"
                for k in _ALU_COMPS:
                    if set(k) == set(ALU):
                        if '-' in ALU:
                            if k == ALU:
                                result += _ALU_COMPS[k]
                                break
                        else:
                            result += _ALU_COMPS[k]
                            break
                
                # For dest
                result += _DESTS[s[0]]
                # No jumps involved
                result += '000'
            else:
                s = line.split(";")
                # ";": comp ; jump
                # For comp
                result += ('1' if "M" in s[0] else '0')
                ALU = s[0].replace("M", "A")
                # "+", "&", "|"
                for k in _ALU_COMPS:
                    if set(k) == set(ALU):
                        if '-' in ALU:
                            if k == ALU:
                                result += _ALU_COMPS[k]
                                break
                        else:
                            result += _ALU_COMPS[k]
                            break

                # No dests involved
                result += '000'
                # For jump
                result += _JUMPS[s[1]]

        result += "\n"
    
    return result


def HackStraightener(line, line_num):
    """
    Syntax checker and code straightener
    Tries to check through all the syntaxes of the code and
    removes all comments, retrieves all labels and attaches them
    with references to their current line number for
    A-instruction to refer to
    """
    global _act_lines
    global _label_con
    result = ""

    line = line.strip("\n")
    # (1) Comments handler
    if line.find("//") >= 0:
        line = line[:line.find("//")]
    # (2) Remove all whitespaces?
    line = line.replace(" ", "").replace("\t", "")

    if line:
        # (3) Check for A-instruction
        if line[0] == "@":
            # Check if it contains character other than _, ., $, 
            # character, digit
            pattern = re.compile(r"[^$:_.0-9a-zA-Z]")
            if re.findall(pattern, line[1:]):
                raise SyntaxError("Line " + str(line_num + 1) + " - Illegal character found")
            else:
                # Check if it starts with number?
                if len(line[1:]) > 1:
                    if line[1].isdigit() and not line[2:].isdigit():
                        raise SyntaxError("Line " + str(line_num + 1) + " - must not begin with digit for non-integer variable")
                _act_lines += 1
                result = line

        # (4) Label for jumping
        # Example: (HAHA), but cannot contain any char outside ()
        elif "(" in line or ")" in line:
            if "(" not in line:
                raise SyntaxError("Line " + str(line_num + 1) + " - Missing \"(\"")
            elif ")" not in line:
                raise SyntaxError("Line " + str(line_num + 1) + " - Missing \")\"")
            else:
                if line[:line.find("(")]:
                    raise SyntaxError("Line " + str(line_num + 1) + " - Text found before \"(\"")
                elif line[line.find(")")+1:]:
                    raise SyntaxError("Line " + str(line_num + 1) + " - Text found after \")\"")
                _label_con[line[line.find("(")+1:line.find(")")]] = _act_lines

        # (5) Check for C-instruction
        # dest = comp ; jump
        # Only following forms can exist:
        # (a) dest = comp
        # (b) comp ; jump
        # Assembly mnemonics: A, D, M (capital letter form)
        else:
            if "=" in line and ";" in line:
                raise SyntaxError("Line " + str(line_num + 1) + " - Either only one \"=\" or \";\" can exist")
            elif "=" in line or ";" in line:
                if "=" in line:
                    # dest = comp
                    components = line.split("=")
                    if len(components) > 2:
                        raise SyntaxError("Line " + str(line_num + 1) + " - Either only one \"=\" or \";\" can exist")

                    ALU = components[1]
                    # dest:
                    if not components[0] in _DESTS:
                        raise SyntaxError("Line " + str(line_num + 1) + " - Wrong destination mnemonics")

                elif ";" in line:
                    # comp ; jump
                    components = line.split(";")
                    if len(components) > 2:
                        raise SyntaxError("Line " + str(line_num + 1) + " - Either only one \"=\" or \";\" can exist")

                    ALU = components[0]
                    # jump:
                    if not components[1] in _JUMPS:
                        raise SyntaxError("Line " + str(line_num + 1) + " - Wrong jump syntax")

                # Dealing with comp (ALU)
                pattern = re.compile(r"^([!-]?[ADM01]|[ADM01][+\-\&|][ADM01])$")
                if re.findall(pattern, ALU):
                    # Since M is from A, replace all the M to A
                    ALU = ALU.replace("M", "A")

                    # Regex has handled most of instruction syntaxes,
                    # except for duplicates like A+A, D+D
                    found = False
                    for k in _ALU_COMPS:
                        if set(k) == set(ALU):
                            if '-' in ALU:
                                if k == ALU:
                                    found = True
                            else:
                                found = True
                        if found:
                            break
                    
                    if not found:
                        raise SyntaxError("Line " + str(line_num + 1) + " - Unknown instruction found")

                else:
                    raise SyntaxError("Line " + str(line_num + 1) + " - Unknown instruction found")

                _act_lines += 1
                result = line
            else:
                raise SyntaxError("Line " + str(line_num + 1) + " - Unknown instruction found")
    return result


def Assembler():
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Error: File name is expected.")
        return 1
    
    pattern = re.compile(r"^[^.]+$|^.+\.asm$")
    s = re.findall(pattern, filename)
    
    if len(s) == 0:
        print("Error: Either file is not found or file name is expected.")
        return 2
    
    s = s[0].rsplit('.', maxsplit=1)[0]

    read_ext = ".asm"
    result_ext = ".hack"
    try:
        asm_file = open(s + read_ext, "r")
        res_file = open(s + result_ext, "w")
    except FileNotFoundError:
        print("Error: File is not found.")
        return 3
    
    res = []
    line_num = 0
    try:
        # Hack Straightener
        for line in asm_file:
            # print(line, end="") # For reference
            r = HackStraightener(line, line_num)
            if r:
                res.append(r)
            line_num += 1

        # Hack Translator
        for line in res:
            res_file.write(HackTranslate(line))
        
    finally:
        asm_file.close()
        res_file.close()

if __name__ == "__main__":
    Assembler()