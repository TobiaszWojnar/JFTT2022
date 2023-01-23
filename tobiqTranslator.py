import tobiqContext_

class TobiqTranslator:
    code = []
    # jumpBackCounter

    def translate(self):
        appendCode = self.code.append
        # TODO check if multi, div, mod
        # TODO Check if każda procedura występuje while(w poprzednim kroku coś wywaliliśmy)
        # TODO if więcej niż zero pracedur
        appendCode("JUMP @MAIN")
        # TODO Check stałe
        # TODO Translator.generate_ready_library(self)
        self.translateProcedures()         # Translator.generate_inner_code(self, lista)

        appendCode("HALT")
        # TODO Fixup jump/callback
        return self.code

    def translateProcedures(self):
        for proc in tobiqContext_.instructions: #REFACTOR TO ADD MULTI, DIV, MOD
            if proc[0] == "PROCEDURE":
                procNameVariables = self.getVarNameInProc(proc[1])
                self.translateBlock(proc[2],proc[1],procNameVariables)
            elif proc[0] == "MAIN":
                procNameVariables = self.getVarNameInProc("MAIN")
                self.translateBlock(proc[1],"MAIN",procNameVariables)


    def translateBlock(self, block, procName,procNameVariables):
        appendCode = self.code.append
        for inst in block:
            if inst[0] == "ASSIGN":
                self.translateAssign(inst[1],inst[2],procName)

            elif inst[0] == "IFELSE":
                appendCode("<if not @{inst[1]} jump_after> [IFELSE]")
                self.translateBlock(inst[2],procName,procNameVariables)
                appendCode("<jump_after next block> [IFELSE]")
                #set_jump_after_1
                self.translateBlock(inst[3],procName,procNameVariables)
                #set_jump_after_2

            elif inst[0] == "IF":
                appendCode("<if not @{inst[1]} jump_after> [IF]")
                self.translateBlock(inst[2],procName,procNameVariables)
                #set_jump_after

            elif inst[0] == "WHILE":
                appendCode("<if not @{inst[1]} jump_out> [WHILE]")# TODO
                self.translateBlock(inst[2],procName,procNameVariables)
                appendCode("JUMP @<jump back while>") #TODO

            elif inst[0] == "REPEAT":
                appendCode("<JUMP back REPEAT>")
                self.translateBlock(inst[2],procName,procNameVariables)
                appendCode("<if @{inst[1]} jump_back> [REPEAT]")# TODO
            
            elif inst[0] == "PROC": # TODO looks ok? ish?
                for i in range(len(inst[2])):
                    appendCode("LOADI @"+inst[2][i])
                    appendCode("STORE @"+procNameVariables[i])
                appendCode("SET @{HERE+2} [JUMP_BACK]")
                appendCode("LOAD @"+procName+"_JUMP")
                appendCode("JUMP @"+procName)
            
            elif inst[0] == "READ":
                appendCode("GET @"+inst[1]+"_"+procName)

            elif inst[0] == "WRITE":
                appendCode("PUT @"+inst[1]+"_"+procName)

            else:
                print("ERROR "+inst)

    def translateAssign(self,identifier,exp,procName):
        appendCode = self.code.append

        if exp[0].isnumeric(): #a:=5
            appendCode("SET "+exp[0])
            appendCode("STORE @"+identifier+"_"+procName)

        elif exp[0] == "add": # TODO when ADDI ? WEWNĄTRZ PROCEDUR?
            appendCode("LOAD @"+exp[1]+"_"+procName)
            appendCode("ADD @"+exp[2]+"_"+procName)
            appendCode("STORE @"+identifier+"_"+procName)

        elif exp[0] == "sub": # TODO when ADDI ?
            appendCode("LOAD @"+exp[1]+"_"+procName)
            appendCode("SUB @"+exp[2]+"_"+procName)
            appendCode("STORE @"+identifier+"_"+procName)

        elif exp[0] == "mul": #TODO for now naive Are variables set? # multi p q
            # acc = 0
            appendCode("SET 0")
            # m = acc
            appendCode("STORE @TMP2")
            # acc = p
            appendCode("LOAD @"+exp[1]+"_"+procName)
            # n = acc
            #TODO should it be a line?
            # if acc = 0 break
            appendCode("JZERO @{HERE+9} [multi x 0, dont even try just return 0]")
            #   acc -1
            appendCode("SUB @1")
            #   n = acc
            appendCode("STORE @TMP1")
            # 	acc = m
            appendCode("LOAD @TMP2")
            # 	acc + q
            appendCode("ADD  @"+exp[2]+"_"+procName)
            # 	m = acc
            appendCode("STORE @TMP2")
            # 	acc = n
            appendCode("LOAD @TMP1")
            # 	jump back if
            appendCode("JZERO @{HERE-6}")
            # acc = m
            appendCode("LOAD @TMP2")
            # id = acc
            appendCode("STORE @"+identifier+"_"+procName)

        elif exp[0] == "div":# div p d

            # result = 0
            appendCode("SET 0")
            appendCode("STORE @TMP1")
            # if d = 0 jump_out
            appendCode("LOAD @"+exp[2]+"_"+procName)
            appendCode("JZERO @")#jump out
            # rest = p
            appendCode("LOAD @"+exp[1]+"_"+procName)
            appendCode("STORE @TMP2")
            # acc = rest - d
            appendCode("SUB @"+exp[2]+"_"+procName)
        # if 0 jump_out
            appendCode("JZERO @")#jump out
            # rest = acc
            appendCode("STORE @TMP2")
            # result + 1
            appendCode("SET 1")
            appendCode("ADD @TMP1")
            appendCode("STORE @TMP1")
            # acc = rest - d
            appendCode("LOAD @TMP2")
            appendCode("SUB @"+exp[2]+"_"+procName)
        # jump_back_if
            appendCode("JUMP @{HERE-7}") #jump back to if
            # id = result
            appendCode("LOAD @TMP1")
            appendCode("STORE @"+identifier+"_"+procName)

        elif exp[0] == "mod": # mod p d

            # result = 0
            appendCode("SET 0")
            appendCode("STORE @TMP1")
            # if d = 0 jump_out
            appendCode("LOAD @"+exp[2]+"_"+procName)
            appendCode("JZERO @")#jump out
            # rest = p
            appendCode("LOAD @"+exp[1]+"_"+procName)
            appendCode("STORE @TMP2")
            # acc = rest - d
            appendCode("SUB @"+exp[2]+"_"+procName)
        # if 0 jump_out
            appendCode("JZERO @")#jump out
            # rest = acc
            appendCode("STORE @TMP2")
            # result + 1
            appendCode("SET 1")
            appendCode("ADD @TMP1")
            appendCode("STORE @TMP1")
            # acc = rest - d
            appendCode("LOAD @TMP2")
            appendCode("SUB @"+exp[2]+"_"+procName)
        # jump_back_if
            appendCode("JUMP @{HERE-7}") #jump back to if
            # id = rest
            appendCode("LOAD @TMP2")
            appendCode("STORE @"+identifier+"_"+procName)

        else:   #a:=b
            appendCode("LOAD @"+exp[0])
            appendCode("STORE @"+identifier+"_"+procName)

    def translateCondition(self,cond,procName):#TODO
        appendCode = self.code.append
        if cond[0] == "eq": # TODO set jumps # TODO set variables
                                        # 2 3       # 3 2
            appendCode("SET 1")         # acc = 1   # acc = 1
            appendCode("ADD @TMP1")     # acc = 2   # acc = 4
            appendCode("SUB @TMP2")     # acc = 0   # acc = 2
            appendCode("JPOS @")        # JUMP OUT  # nothing
            appendCode("SUB 1")         #           # acc = 1
            appendCode("JPOS @")        #           # JUMP OUT
            appendCode("JUMP @")        #  True only on this line
            
        elif cond[0] == "ne":  # TODO set jumps
                                        # 3 4           # 5 4
            appendCode("SET 1")         # acc = 1       # acc = 1
            appendCode("ADD @TMP1")     # acc = 4       # acc = 6
            appendCode("SUB @TMP2")     # acc = 0       # acc = 2
            appendCode("JZERO ")        # NOT jump_out  # NO action
            appendCode("SUB 1")         # acc = 0       # acc = 1
            appendCode("JPOS ")         #               # NOT jump_out
            # appendCode(cond)
        elif cond[0] == "gt":  # TODO set jumps

            appendCode("LOAD @TMP1")
            appendCode("SUB @TMP2")
            appendCode("JPOS [not true]")
            appendCode("JUMP [true]")
            # appendCode(cond)

        elif cond[0] == "ge":  # TODO set jumps

            appendCode("SET 1")
            appendCode("ADD @TMP1")
            appendCode("SUB @TMP2")
            appendCode("JPOS [not true]")
            appendCode("JUMP [true]")
            # appendCode(cond)
        else:
            appendCode("ERROR "+cond)


    def getVarNameInProc(self,procName):
        result=[]
        for var in tobiqContext_.variablesNames:
            if var.startswith(procName):
                result.append(var)
        return result