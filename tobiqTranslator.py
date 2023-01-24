import tobiqContext_

class TobiqTranslator:
    code = []

    def translate(self):
        appendCode = self.code.append
        appendCode("JUMP @MAIN")
        self.translateProcedures()
        appendCode("HALT")
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
                if procName=="MAIN":
                    self.translateAssignMAIN(inst[1],inst[2],procName)
                else:
                    self.translateAssignPROC(inst[1],inst[2],procName)

            elif inst[0] == "IFELSE":
                tmpPointerFalse = "NEW_Pointer_F+1"
                tmpPointerTrue = "NEW_Pointer_T+1"
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"IFELSE",tmpPointerFalse)
                # else:
                #     self.translateAssignPROC(inst[1],inst[2],procName)
                self.translateBlock(inst[2],procName,procNameVariables)
                appendCode("JUMP @"+tmpPointerTrue+"    ["+tmpPointerFalse+"]")
                self.translateBlock(inst[3],procName,procNameVariables)
                self.code[-1]+=("  ["+tmpPointerTrue+"]")

            elif inst[0] == "IF":
                tmpPointer = "NEW_Pointer+1"
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"IF",tmpPointer)
                # else:
                #     self.translateAssignPROC(inst[1],inst[2],procName)
                self.translateBlock(inst[2],procName,procNameVariables)
                
                self.code[-1].append("  ["+tmpPointer+"]") #TODO check

            elif inst[0] == "WHILE":
                tmpPointer = "NEW_Pointer+1"
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"$HERE_While",tmpPointer)
                # else:
                #     self.translateAssignPROC(inst[1],inst[2],procName)
                self.translateBlock(inst[2],procName,procNameVariables)
                appendCode("JUMP @HERE_While    ["+tmpPointer+"]") #TODO

            elif inst[0] == "REPEAT":
                tmpPointerBack = "JUMP_back_REPEAT+1"
                tmpPointerOut = "JUMP_out_REPEAT+1"
                self.code[-1].append("  [$"+tmpPointerBack+"]") 
                self.translateBlock(inst[2],procName,procNameVariables)
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"Until",tmpPointerOut)
                # else:
                #     self.translateAssignPROC(inst[1],inst[2],procName)
                appendCode("JUMP @"+tmpPointerBack)
            
            elif inst[0] == "PROC": # DONE (hope so)
                for i in range(len(inst[2])):
                    appendCode("SET @"+inst[2][i]+"_"+procName)
                    appendCode("STORE @"+procNameVariables[i])
                appendCode("SET @{HERE+2} [JUMP_BACK after procedure]")
                appendCode("STORE @"+procName+"_JUMP")
                appendCode("JUMP @"+procName) #TODO JUMP
            
            elif inst[0] == "READ": #TODO if not in main
                appendCode("GET @"+inst[1]+"_"+procName)

            elif inst[0] == "WRITE": #TODO if not in main
                appendCode("PUT @"+inst[1]+"_"+procName)

            else:
                print("ERROR "+inst)


    def translateAssignMAIN(self,identifier,exp,procName):
        appendCode = self.code.append

        if exp[0].isnumeric(): #a:=5
            appendCode("SET "+exp[0])
            appendCode("STORE @"+identifier+"_"+procName)

        elif exp[0] == "add": 
            appendCode("LOAD @"+exp[1]+"_"+procName)
            appendCode("ADD @"+exp[2]+"_"+procName)
            appendCode("STORE @"+identifier+"_"+procName)

        elif exp[0] == "sub":
            appendCode("LOAD @"+exp[1]+"_"+procName)
            appendCode("SUB @"+exp[2]+"_"+procName)
            appendCode("STORE @"+identifier+"_"+procName)

        elif exp[0] == "mul": #TODO for now naive Are variables set? # multi p q
            
            appendCode("SET 0               [MULTI BEGIN]") # acc = 0
            appendCode("STORE @TMP2")                       # m = acc
            appendCode("LOAD @"+exp[1]+"_"+procName)        # acc = p
                                                            # n = acc
                                                            #TODO should it be a line?
            appendCode("JZERO @{HERE+9} [multi x 0, dont even try just return 0]") # if acc = 0 break
            appendCode("SUB @1")                            # acc -1
            appendCode("STORE @TMP1")                       # n = acc
            appendCode("LOAD @TMP2")                        # acc = m
            appendCode("ADD  @"+exp[2]+"_"+procName)        # acc + q
            appendCode("STORE @TMP2")                       # m = acc
            appendCode("LOAD @TMP1")                        # acc = n
            appendCode("JZERO @{HERE-6}")                   # jump back if
            appendCode("LOAD @TMP2")                        # acc = m
            appendCode("STORE @"+identifier+"_"+procName+"[MULTI END]")  # id = acc

        elif exp[0] == "div":# div p d

            appendCode("SET 0")                     # result = 0
            appendCode("STORE @TMP1")
            appendCode("LOAD @"+exp[2]+"_"+procName)# if d = 0 jump_out
            appendCode("JZERO @")#jump out
            appendCode("LOAD @"+exp[1]+"_"+procName)# rest = p
            appendCode("STORE @TMP2")
            appendCode("SUB @"+exp[2]+"_"+procName) # acc = rest - d
            appendCode("JZERO @")                   # if 0 jump_out
            appendCode("STORE @TMP2")               # rest = acc
            appendCode("SET 1")                     # result + 1
            appendCode("ADD @TMP1")
            appendCode("STORE @TMP1")               # acc = rest - d
            appendCode("LOAD @TMP2")
            appendCode("SUB @"+exp[2]+"_"+procName)
            appendCode("JUMP @{HERE-7}")            #jump back to if
            appendCode("LOAD @TMP1")                # id = result
            appendCode("STORE @"+identifier+"_"+procName)

        elif exp[0] == "mod": # mod p d

            appendCode("SET 0")                         # result = 0
            appendCode("STORE @TMP1")
            appendCode("LOAD @"+exp[2]+"_"+procName)    # if d = 0 jump_out
            appendCode("JZERO @")                       #jump out
            appendCode("LOAD @"+exp[1]+"_"+procName)    # rest = p
            appendCode("STORE @TMP2")                   # acc = rest - d
            appendCode("SUB @"+exp[2]+"_"+procName)
            appendCode("JZERO @")                       # if 0 jump_out 
            appendCode("STORE @TMP2")                   # rest = acc
            appendCode("SET 1")                         # result + 1
            appendCode("ADD @TMP1")
            appendCode("STORE @TMP1")
            appendCode("LOAD @TMP2")                    # acc = rest - d
            appendCode("SUB @"+exp[2]+"_"+procName)
            appendCode("JUMP @{HERE-7}")                # jump back to if
            appendCode("LOAD @TMP2")                    # id = rest
            appendCode("STORE @"+identifier+"_"+procName)

        else:   #a:=b
            appendCode("LOAD @"+exp[0]+"_"+procName)
            appendCode("STORE @"+identifier+"_"+procName)


    def translateAssignPROC(self,identifier,exp,procName):
        appendCode = self.code.append

        if exp[0].isnumeric(): #a:=5
            appendCode("SET "+exp[0])
            appendCode("STOREI @"+identifier+"_"+procName)

        elif exp[0] == "add":
            appendCode("LOADI @"+exp[1]+"_"+procName)
            appendCode("ADDI @"+exp[2]+"_"+procName)
            appendCode("STOREI @"+identifier+"_"+procName)

        elif exp[0] == "sub":
            appendCode("LOADI @"+exp[1]+"_"+procName)
            appendCode("SUBI @"+exp[2]+"_"+procName)
            appendCode("STOREI @"+identifier+"_"+procName)

        elif exp[0] == "mul": #TODO for now naive Are variables set? # multi p q
            
            appendCode("SET 0")                             # acc = 0
            appendCode("STOREI @TMP2")                      # m = acc
            appendCode("LOADI @"+exp[1]+"_"+procName)       # acc = p
                                                            # n = acc
                                                            #TODO should it be a line?
                                                            # if acc = 0 break
            appendCode("JZERO @{HERE+9} [multi x 0, dont even try just return 0]")
            appendCode("SUBI @1")                           #   acc -1
            appendCode("STOREI @TMP1")                      #   n = acc
            appendCode("LOADI @TMP2")                       # 	acc = m
            appendCode("ADDI @"+exp[2]+"_"+procName)        # 	acc + q
            appendCode("STOREI @TMP2")                      # 	m = acc
            appendCode("LOADI @TMP1")                       # 	acc = n
            appendCode("JZERO @{HERE-6}")                   # 	jump back if
            appendCode("LOADI @TMP2")                       # acc = m
            appendCode("STOREI @"+identifier+"_"+procName)  # id = acc

        elif exp[0] == "div":# div p d

            appendCode("SET 0")                             # result = 0
            appendCode("STOREI @TMP1")
            appendCode("LOADI @"+exp[2]+"_"+procName)       # if d = 0 jump_out
            appendCode("JZERO @")                           # jump out
            appendCode("LOADI @"+exp[1]+"_"+procName)       # rest = p
            appendCode("STOREI @TMP2")
            appendCode("SUBI @"+exp[2]+"_"+procName)        # acc = rest - d
            appendCode("JZERO @")                           # if 0 jump_out
            appendCode("STOREI @TMP2")                      # rest = acc
            appendCode("SET 1")                             # result + 1
            appendCode("ADDI @TMP1")
            appendCode("STOREI @TMP1")
            appendCode("LOADI @TMP2")                       # acc = rest - d
            appendCode("SUBI @"+exp[2]+"_"+procName)
            appendCode("JUMP @{HERE-7}")                    #jump back to if
            appendCode("LOADI @TMP1")                       # id = result
            appendCode("STOREI @"+identifier+"_"+procName)

        elif exp[0] == "mod": # mod p d

            appendCode("SET 0")                         # result = 0
            appendCode("STOREI @TMP1")
            appendCode("LOADI @"+exp[2]+"_"+procName)   # if d = 0 jump_out
            appendCode("JZERO @")                       #jump out
            appendCode("LOADI @"+exp[1]+"_"+procName)   # rest = p
            appendCode("STORE @TMP2")
            appendCode("SUBI @"+exp[2]+"_"+procName)    # acc = rest - d
            appendCode("JZERO @")                       # if 0 jump_out
            appendCode("STOREI @TMP2")                  # rest = acc
            appendCode("SET 1")                         # result + 1
            appendCode("ADDI @TMP1")
            appendCode("STOREI @TMP1")
            appendCode("LOADI @TMP2")                   # acc = rest - d
            appendCode("SUBI @"+exp[2]+"_"+procName)
            appendCode("JUMP @{HERE-7}")                #jump back to if
            appendCode("LOADI @TMP2")                   # id = rest
            appendCode("STOREI @"+identifier+"_"+procName)

        else:   #a:=b
            appendCode("LOADI @"+exp[0])
            appendCode("STOREI @"+identifier+"_"+procName)


    def translateConditionMAIN(self,cond,procName,codePointer,jumpF):
        appendCode = self.code.append
        if cond[0] == "eq":
                                                        # 2 3       # 3 2
            appendCode("SET 1 [$"+codePointer+"]")      # acc = 1   # acc = 1
            appendCode("ADD @"+procName+"_"+cond[1])    # acc = 2   # acc = 4
            appendCode("SUB @"+procName+"_"+cond[2])    # acc = 0   # acc = 2
            appendCode("JPOS @"+jumpF)                  # JUMP OUT  # nothing
            appendCode("SUB @1")                        #           # acc = 1
            appendCode("JPOS @"+jumpF)                  #           # JUMP OUT
            # appendCode("JUMP @"+jumpT)                #  True only on this line
            
        elif cond[0] == "ne":  # TODO set jumps
                                                        # 3 4           # 5 4
            appendCode("SET 1 [$"+codePointer+"]")      # acc = 1       # acc = 1
            appendCode("ADD @"+procName+"_"+cond[1])    # acc = 4       # acc = 6
            appendCode("SUB @"+procName+"_"+cond[2])    # acc = 0       # acc = 2
            appendCode("JZERO @"+jumpF)                 # NOT jump_out  # NO action
            appendCode("SUB @1")                        # acc = 0       # acc = 1
            appendCode("JPOS @"+jumpF)                  #               # NOT jump_out
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        elif cond[0] == "gt":   # 

            appendCode("LOAD @"+procName+"_"+cond[1]+"  [$"+codePointer+"]")
            appendCode("SUB @"+procName+"_"+cond[2])
            appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)

        elif cond[0] == "ge":  # TODO set jumps

            appendCode("SET 1 [$"+codePointer+"]")
            appendCode("ADD @"+procName+"_"+cond[1])
            appendCode("SUB @"+procName+"_"+cond[2])
            appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        else:
            appendCode("ERROR "+cond)

    def translateConditionPROC(self,cond,procName,codePointer,jumpF): #TODO
        appendCode = self.code.append
        if cond[0] == "eq":
                                                        # 2 3       # 3 2
            appendCode("SET 1 [$"+codePointer+"]")      # acc = 1   # acc = 1
            appendCode("ADD @"+procName+"_"+cond[1])    # acc = 2   # acc = 4
            appendCode("SUB @"+procName+"_"+cond[2])    # acc = 0   # acc = 2
            appendCode("JPOS @"+jumpF)                  # JUMP OUT  # nothing
            appendCode("SUB @1")                        #           # acc = 1
            appendCode("JPOS @"+jumpF)                  #           # JUMP OUT
            # appendCode("JUMP @"+jumpT)                #  True only on this line
            
        elif cond[0] == "ne":  # TODO set jumps
                                                        # 3 4           # 5 4
            appendCode("SET 1 [$"+codePointer+"]")      # acc = 1       # acc = 1
            appendCode("ADD @"+procName+"_"+cond[1])    # acc = 4       # acc = 6
            appendCode("SUB @"+procName+"_"+cond[2])    # acc = 0       # acc = 2
            appendCode("JZERO @"+jumpF)                 # NOT jump_out  # NO action
            appendCode("SUB @1")                        # acc = 0       # acc = 1
            appendCode("JPOS @"+jumpF)                  #               # NOT jump_out
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        elif cond[0] == "gt":   # 

            appendCode("LOAD @"+procName+"_"+cond[1]+"  [$"+codePointer+"]")
            appendCode("SUB @"+procName+"_"+cond[2])
            appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)

        elif cond[0] == "ge":  # TODO set jumps

            appendCode("SET 1 [$"+codePointer+"]")
            appendCode("ADD @"+procName+"_"+cond[1])
            appendCode("SUB @"+procName+"_"+cond[2])
            appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        else:
            appendCode("ERROR "+cond)


    def getVarNameInProc(self,procName):
        result=[]
        for var in tobiqContext_.variablesNames:
            if var.startswith(procName):
                result.append(var)
        return result