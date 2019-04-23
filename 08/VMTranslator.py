"""
VM to HACK Translator Python
"""

import sys
import re
import os

_PUSH_POP = ['push','pop']
_DOUBLE_OP = ['add','sub','and','or','gt','eq','lt']
_SINGLE_OP = ['not','neg']
_SEGMENTS = {'static':"16",'constant':'','local':'LCL','argument':'ARG',
             'this':'THIS','that':'THAT','pointer':['THIS','THAT'],'temp':"5",
             "#13":"R13","#14":"R14","#15":"R15"}
_FLOW_OP = ['label','if-goto','goto']
_FUNC_OP = ['function','call','return']

_VM_EXT = ".vm"
_VM_SYS = "Sys"

# For VMParser:
_func_store = {}
_jump_counter = 0

# For all:
_static_store = {}


def PathTargetCheck(dir_path, target_name, is_vm_file=True):
    """
    Checking for the path of file
    is_vm_file = False if the file is a directory
    """
    path_target = dir_path + target_name

    if is_vm_file:
        if not os.path.isfile(path_target + _VM_EXT):
            raise FileNotFoundError("Error: " + target_name + _VM_EXT + " not found.")
    else:
        # If getcwd is directly the target name, just directly find the Sys.vm
        if os.path.basename(os.getcwd()) == path_target:
            if not os.path.isfile(_VM_SYS + _VM_EXT):
                raise FileNotFoundError("Error: " + _VM_SYS + _VM_EXT + " in directory " + target_name + " not found.")
        else:
            if os.path.isdir(path_target):
                if not os.path.isfile(path_target + "/" + _VM_SYS + _VM_EXT):
                    raise FileNotFoundError("Error: " + _VM_SYS + _VM_EXT + " in directory " + target_name + " not found.")
            else:
                raise FileNotFoundError("Error: Directory " + target_name + " not found.")


def VMParser(dir_path, target_name):
    """
    To output the codes after syntax checking and essential components storage
    """

    result = []
    
    path_target = dir_path + target_name
    vm_file = open(path_target + _VM_EXT, "r")

    # To store the codes from called function, if found
    call_comm = []

    # To store called functions for checking
    func_check = {}

    # To store labels
    labels = {}
    label_check = {}

    line_num = 1
    for line in vm_file:
        line = line.strip(' \n')
        
        # Comments handler
        if line.find("//") >= 0:
            line = line[:line.find("//")]

        if line:
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
                    raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Too few arguments in " + comm[0] + ".")
                elif len(comm) > 3:
                    raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Too many arguments in " + comm[0] + ".")

                if comm[0] == 'pop' and comm[1] == 'constant':
                    raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Constant cannot be used in pop.")
                    
                if comm[1] in _SEGMENTS:
                    if not comm[2]:
                        raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Missing non-negative integers in " + comm[0] + ".")
                    else:
                        if not comm[2].isdigit():
                            raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + comm[0].capitalize() + " only allows integers.")
                        elif int(comm[2]) < 0:
                            raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + comm[0].capitalize() + " only allows non-negative integers.")
                        
                        if comm[1] == 'pointer' and int(comm[2]) >= 2:
                            raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + comm[1] + " only allows 0/1 in " + comm[0] + ".")

                        # To store the max number of static parameter of target file
                        if comm[1] == 'static':
                            # To store static variable count for each unique file
                            global _static_store

                            if target_name not in _static_store:
                                _static_store[target_name] = int(comm[2]) + 1
                            else:
                                if (int(comm[2]) + 1) > _static_store[target_name]:
                                    _static_store[target_name] = int(comm[2]) + 1
                                    
                else:
                    raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Unrecognised segment.")

            elif comm[0] in _DOUBLE_OP + _SINGLE_OP:
                if len(comm) > 1:
                    raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Too many arguments.")

            elif comm[0] in _FLOW_OP:
                if len(comm) > 2:
                    raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Too many arguments.")
                elif len(comm) < 2:
                    raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Missing label.")
                
                # Store labels in jumping into label list, delete them if found
                if comm[0] == 'label':
                    if comm[1] in label_check:
                        del label_check[comm[1]]
                    labels[comm[1]] = line_num - 1
                else:
                    if comm[1] not in labels:
                        label_check[comm[1]] = line_num
            
            elif comm[0] in _FUNC_OP:
                if comm[0] == 'return':
                    if len(comm) > 1:
                        raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Too many arguments.")
                else:
                    if len(comm) > 3:
                        raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Too many arguments.")
                    elif len(comm) < 3:
                        raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Too few arguments.")

                    file_comps = comm[1].split('.')
                    if len(file_comps) < 2 or len(file_comps) > 2:
                        raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - \"" + comm[1] + "\" is an invalid function name.")
                    else:
                        if not file_comps[0] or not file_comps[1]:
                            raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - \"" + comm[1] + "\" is an invalid function name.")

                    if not comm[2].isdigit():
                        raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + comm[0].capitalize() + " only allows integers.")
                    elif int(comm[2]) < 0:
                        raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + comm[0].capitalize() + " only allows non-negative integers.")

                    if comm[0] == 'function':
                        global _func_store

                        if file_comps[0] != target_name:
                            raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - \"" + file_comps[0] + "\" is not same as file name.")
                        
                        if file_comps[0] not in _func_store:
                            # If file is not found, create the list and store the func name
                            _func_store[file_comps[0]] = [file_comps[1]]
                        else:
                            # Duplicate function definition
                            if file_comps[1] in _func_store[file_comps[0]]:
                                raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Duplicate function " + comm[1] + " found.")

                            # Else, append/store the func name
                            _func_store[file_comps[0]].append(file_comps[1])
                    else:
                        if file_comps[0] != target_name:
                            # To prevent infinite recursion
                            if file_comps[0] not in _func_store:
                                PathTargetCheck(dir_path, file_comps[0])
                                call_comm.extend(VMParser(dir_path, file_comps[0]))

                            if file_comps[1] not in _func_store[file_comps[0]]:
                                raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Function " + comm[1] + " not found.")
                        else:
                            # On the same file, add the calling function into dict for further checking
                            if file_comps[1] not in func_check:
                                func_check[file_comps[1]] = line_num

            else:
                raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(line_num) + " - " + "Unrecognised command.")

            result.append(comm)

        line_num += 1
    
    # Goto target not found
    if label_check:
        raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(list(label_check.values())[0]) + " - " + "Unknown goto target \"" + list(label_check)[0] + "\".")
    
    # Called function does not exist
    for func in func_check:
        if func not in _func_store[target_name]:
            raise SyntaxError("In " + target_name + _VM_EXT + ": Line " + str(func_check[func]) + " - " + "Function " + target_name + "." + func + " not found.")

    if call_comm:
        result.extend(call_comm)

    return result


def ASMCodeWriter(parsed, init):
    """
    ASM Code Writer:
    Outputs appropriate assembly codes based on parsed inputs from
    the Parser
    """

    result = ""
    curr_func = ""

    # For function return unique ID count
    ret_id = 0

    # For static variables unique ID count
    global _static_store
    static_counter = 16

    def push_pop(comms):
        """
        Implementation of push and pop memory access actions
        Common segments: constant, pointer, local, argument, temp, this, that, static
        Special: #etc
        """
        nonlocal result
        nonlocal static_counter

        segment, val = comms[1:]
        # PUSH
        if comms[0] == "push":
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
            elif segment in ["static", "temp"]:
                # Static: special case
                if segment == "static":
                    seg = "@" + str(static_counter)
                else:
                    seg = "@" + _SEGMENTS[segment]
                result += '\n'.join((
                    seg,
                    "D=A",
                    "@" + val,
                    "A=A+D",
                    "D=M"
                ))
            elif segment in ["local", "argument", "this", "that"]:
                result += '\n'.join((
                    "@" + _SEGMENTS[segment],
                    "D=M",
                    "@" + val,
                    "A=A+D",
                    "D=M"
                ))
            elif segment == "#etc":
                # Custom made segment maker
                result += '\n'.join((
                    "@" + val,
                    "D=M",
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
            if segment == "pointer":
                result += '\n'.join((
                    "@" + _SEGMENTS[segment][int(val)],
                    "D=A"
                ))
            elif segment in ["static", "temp"]:
                # Static: special case
                if segment == "static":
                    seg = "@" + str(static_counter)
                else:
                    seg = "@" + _SEGMENTS[segment]
                result += '\n'.join((
                    seg,
                    "D=A",
                    "@" + val,
                    "D=A+D"
                ))
            elif segment in ["local", "argument", "this", "that"]:
                result += '\n'.join((
                    "@" + _SEGMENTS[segment],
                    "D=M",
                    "@" + val,
                    "D=A+D"
                ))
            elif segment == "#etc":
                result += '\n'.join((
                    "@" + val,
                    "D=A",
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
        result += '\n'
    
    def arithmetics(comms):
        """
        Implementation of arithmetic (add, sub, neg) and 
        logical commands (gt, lt, eq, and, or, not)
        """
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
                    "M=1",
                    "@" + curr_func + "$LG$JUMP" + str(_jump_counter),
                    "D;JGT" if comms[0] == "gt" else (
                        "D;JEQ" if comms[0] == "eq" else "D;JLT"
                    ),
                    # If false, this is reachable
                    "@SP",
                    "A=M-1",
                    "M=0",
                    "(" + curr_func + "$LG$JUMP" + str(_jump_counter) + ")"
                ))

                _jump_counter += 1
        else:
            result += '\n'.join((
                "@SP",
                "A=M-1",
                "M=!M"
            ))
            if comms[0] == "neg":
                result += '\n' + "M=M+1"
        result += '\n'

    def flowing(comms, special=False):
        """
        Implementation of if-goto, goto, label
        Syntax:
        ["if-goto"/"goto"/"label", LABEL], special
        special: only function name
        """
        nonlocal result

        if comms[0] == "label":
            if special:
                result += "(" + comms[1] + ")"
            else:
                result += "(" + curr_func + "$" + comms[1] + ")"
        elif comms[0] == "goto":
            result += '\n'.join((
                "@" + comms[1] if special else (
                    "@" + curr_func + "$" + comms[1]
                ),
                "0;JMP"
            ))
        elif comms[0] == "if-goto":
            result += '\n'.join((
                # Pop to check the value
                "@SP",
                "AM=M-1",
                "D=M",
                "@" + comms[1] if special else (
                    "@" + curr_func + "$" + comms[1]
                ),
                "D;JGT"
            ))
        result += '\n'

    def functionator(comms):
        """
        Implementation of functions definitions, callings, returns and 
        memory address managements
        """
        nonlocal result
        nonlocal curr_func
        nonlocal static_counter
        nonlocal ret_id

        if comms[0] == "function":
            # Initialise the static variables
            curr_file = curr_func.split(".")[0]
            if curr_file in _static_store:
                if not curr_func:
                    static_counter = 16
                else:
                    if comms[1].split('.')[0] != curr_file:
                        static_counter += int(_static_store[curr_file])
            
            curr_func, num_vars = comms[1:]

            # Put function label
            flowing(["label", curr_func], True)

            # Initialise specified number of local variables to 0
            for _ in range(int(num_vars)):
                push_pop(["push", "constant", "0"])
            
        elif comms[0] == "call":
            call_func, num_args = comms[1:]
            
            # Save all the 5 states (return address, LCL, ARG, THIS, THAT)
            # Assuming "function" is called before "call" is called
            push_pop(["push", "constant", curr_func + "$" + "RET$" + str(ret_id)])
            push_pop(["push", "#etc", _SEGMENTS["local"]])
            push_pop(["push", "#etc", _SEGMENTS["argument"]])
            push_pop(["push", "#etc", _SEGMENTS["this"]])
            push_pop(["push", "#etc", _SEGMENTS["that"]])
            
            result += '\n'.join((
                # Set ARG to before the 5 states and specified number of arguments
                "@5",
                "D=A",
                "@" + num_args,
                "D=A+D",
                "@SP",
                "D=M-D",
                "@" + _SEGMENTS["argument"],
                "M=D",
                # Set LCL to current SP
                "@SP",
                "D=M",
                "@" + _SEGMENTS["local"],
                "M=D"
            ))
            result += '\n'

            # Jump to the called function
            flowing(["goto", call_func], True)

            # Write the return address label
            flowing(["label", "RET$" + str(ret_id)])
            ret_id += 1
        else:
            # Get the starting point (LCL) into R13 as temp
            result += '\n'.join((
                "@" + _SEGMENTS["local"],
                "D=M",
                "@" + _SEGMENTS["#13"],
                "M=D"
            ))
            result += '\n'
            
            # Pop the return value into R14 as temp
            # Because if the function has 0 argument, current
            # ARG points to return address
            # So, direct popping will overwrite the return address 
            push_pop(["pop", "#etc", _SEGMENTS["#14"]])

            # Restore SP to the state of previous function calling
            result += '\n'.join((
                "@" + _SEGMENTS["argument"],
                "D=M",
                "@SP",
                "M=D",
            ))
            result += '\n'

            # RESTORE STATES
            # To reuse R13 to store the return address
            state_segs = ["that", "this", "argument", "local", "#13"]
            for i in range(len(state_segs)):
                result += '\n'.join((
                    "@" + _SEGMENTS["#13"],
                    "D=M",
                    "@" + str(i + 1),
                    "A=D-A",
                    "D=M",
                    "@" + _SEGMENTS[state_segs[i]],
                    "M=D"
                ))
                result += '\n'
            
            # Push the return value from R14
            push_pop(["push", "#etc", _SEGMENTS["#14"]])

            # JUMP TO RETURN ADDRESS
            result += '\n'.join((
                "@" + _SEGMENTS["#13"],
                "A=M",
                "0;JMP"
            ))
        result += '\n'

    # Bootstrap coder
    if init:
        # SP = 256
        result += '// SP = 256' + '\n'
        result += '\n'.join((
            "@256",
            "D=A",
            "@SP",
            "M=D",
        ))
        result += '\n'
        
        # call Sys.init
        result += '// call Sys.init 0' + '\n'
        functionator(["call", "Sys.init", "0"])

    for comms in parsed:
        # Debug: print the VM code in comment form:
        result += '// ' + ' '.join(comms) + '\n'

        # Send commands to appropriate channels
        if comms[0] in _PUSH_POP:
            push_pop(comms)
        elif comms[0] in _DOUBLE_OP + _SINGLE_OP:
            arithmetics(comms)
        elif comms[0] in _FLOW_OP:
            flowing(comms)
        elif comms[0] in _FUNC_OP:
            functionator(comms)
    
    return result


def VMTranslator():
    # Check if the input is a vm file or directory
    # Without .vm, it finds for directory first, tries to find Sys.vm
    # Within Sys.vm, sys.init must be present inside
    try:
        assert len(sys.argv) == 2

        file_target = sys.argv[1].rsplit(_VM_EXT, 1)

        p = re.compile(r"(.*[\\/])(.+)")
        r = re.search(p, file_target[0])
        if r:
            dir_path, target_name = r.groups()
        else:
            dir_path, target_name = "", file_target[0]

        initialisor = False
        if len(file_target) > 1:
            # It is a vm file
            PathTargetCheck(dir_path, target_name)

            # VM parser and ASM file have same target file name
            asm_file_name = dir_path + target_name + ".asm"
        else:
            # It is a directory, gives Sys.vm
            PathTargetCheck(dir_path, target_name, False)
            
            # ASM file has target file name
            asm_file_name = dir_path + target_name + "/" + target_name + ".asm"

            dir_path += target_name + "/"
            target_name = _VM_SYS

            # Initialise bootstrap code
            initialisor = True

        global _func_store
        _func_store = {}

        parsed = VMParser(dir_path, target_name)

        decoded = ASMCodeWriter(parsed, initialisor)
        
        f = open(asm_file_name, "w")
        f.write(decoded)
        f.close()

        print("VM translation succeeded.")
    except (AssertionError, SyntaxError, FileNotFoundError) as err:
        if type(err).__name__ == "AssertionError":
            print("Error: Bad or missing VM file parameter.")
        else:
            print(err)
        print("VM translation failed.")

if __name__ == "__main__":
    VMTranslator()

    ## To be used to open multiple files:
    # f = open("testfile.txt", "r")
    # for line in f:
    #     print(line, end="")
    #     exec(line)
    #     print("")
    # f.close()