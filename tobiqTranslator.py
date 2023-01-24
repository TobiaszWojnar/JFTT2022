import tobiqContext_

class TobiqTranslator:
    code = []

    def translate(self):
        appendCode = self.code.append
        appendCode("JUMP @MAIN")
        self.translateProcedures()
        appendCode("HALT")

        self.evalVariables()

        return self.code

    def translateProcedures(self):
        for proc in tobiqContext_.instructions:
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
                #     self.translateConditionPROC(inst[1],inst[2],procName)
                self.translateBlock(inst[2],procName,procNameVariables)
                appendCode("JUMP @"+tmpPointerTrue+"    ["+tmpPointerFalse+"]")
                self.translateBlock(inst[3],procName,procNameVariables)
                self.code[-1]+=("  ["+tmpPointerTrue+"]")

            elif inst[0] == "IF":
                tmpPointer = "NEW_Pointer+1"
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"IF",tmpPointer)
                # else:
                #     self.translateConditionPROC(inst[1],inst[2],procName)
                self.translateBlock(inst[2],procName,procNameVariables)
                
                self.code[-1]+="  ["+tmpPointer+"]" #TODO check

            elif inst[0] == "WHILE":
                tmpPointer = "NEW_Pointer+1"
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"$HERE_While",tmpPointer)
                # else:
                #     self.translateConditionPROC(inst[1],inst[2],procName)
                self.translateBlock(inst[2],procName,procNameVariables)
                appendCode("JUMP @HERE_While    ["+tmpPointer+"]") #TODO

            elif inst[0] == "REPEAT":
                tmpPointerBack = "JUMP_back_REPEAT+1"
                tmpPointerOut = "JUMP_out_REPEAT+1"
                self.code[-1]+="  [$"+tmpPointerBack+"]"
                self.translateBlock(inst[2],procName,procNameVariables)
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"Until",tmpPointerOut)
                # else:
                #     self.translateConditionPROC(inst[1],inst[2],procName)
                appendCode("JUMP @"+tmpPointerBack)
            
            elif inst[0] == "PROC": # DONE (hope so)
                for i in range(len(inst[2])):
                    appendCode("SET @"+procName+"_"+inst[2][i])
                    appendCode("STORE @"+procNameVariables[i])
                appendCode("SET @{HERE+2} [JUMP_BACK after procedure]")
                appendCode("STORE @"+procName+"_JUMP")
                appendCode("JUMP @"+procName) #TODO JUMP
            
            elif inst[0] == "READ": 
                if procName=="MAIN":
                    appendCode("GET @"+procName+"_"+inst[1])
                else:
                    appendCode("GET @"+procName+"_"+inst[1])#TODO if not in main

            elif inst[0] == "WRITE":
                if procName=="MAIN":
                    appendCode("PUT @"+procName+"_"+inst[1])
                else:
                    appendCode("LOADI @"+procName+"_"+inst[1])
                    appendCode("PUT 0")

            else:
                print("ERROR "+inst)


    def translateAssignMAIN(self,identifier,exp,procName):
        appendCode = self.code.append

        if exp[1].isnumeric():
            exp1 = exp[1]
        else:
            exp1 = procName+"_"+exp[1]
        if exp[2].isnumeric():
            exp2 = exp[2]
        else:
            exp2 = procName+"_"+exp[2]


        if exp[0].isnumeric(): #a:=5
            appendCode("SET "+exp[0])
            appendCode("STORE @"+procName+"_"+identifier)

        elif exp[0] == "add": 
            appendCode("LOAD @"+exp1)
            appendCode("ADD @"+exp2)
            appendCode("STORE @"+procName+"_"+identifier)

        elif exp[0] == "sub":
            appendCode("LOAD @"+exp1)
            appendCode("SUB @"+exp2)
            appendCode("STORE @"+procName+"_"+identifier)

        elif exp[0] == "mul": # multi p q
            
            appendCode("SET 0               [MULTI BEGIN]") # acc = 0
            appendCode("STORE @TMP2")                       # m = acc
            appendCode("LOAD @"+exp1)        # acc = p
                                                            # n = acc
                                                            # should it be a line?
            appendCode("JZERO @{HERE+9} [multi x 0, dont even try just return 0]") # if acc = 0 break
            appendCode("SUB @1")                            # acc -1
            appendCode("STORE @TMP1")                       # n = acc
            appendCode("LOAD @TMP2")                        # acc = m
            appendCode("ADD  @"+exp2)        # acc + q
            appendCode("STORE @TMP2")                       # m = acc
            appendCode("LOAD @TMP1")                        # acc = n
            appendCode("JZERO @{HERE-6}")                   # jump back if
            appendCode("LOAD @TMP2")                        # acc = m
            appendCode("STORE @"+procName+"_"+identifier+"[MULTI END]")  # id = acc

        elif exp[0] == "div":# div p d

            appendCode("SET 0")                     # result = 0
            appendCode("STORE @TMP1")
            appendCode("LOAD @"+exp2)# if d = 0 jump_out
            appendCode("JZERO @")                   #jump out
            appendCode("LOAD @"+exp1)# rest = p
            appendCode("STORE @TMP2")
            appendCode("SUB @"+exp2) # acc = rest - d
            appendCode("JZERO @")                   # if 0 jump_out
            appendCode("STORE @TMP2")               # rest = acc
            appendCode("SET 1")                     # result + 1
            appendCode("ADD @TMP1")
            appendCode("STORE @TMP1")               # acc = rest - d
            appendCode("LOAD @TMP2")
            appendCode("SUB @"+exp2)
            appendCode("JUMP @{HERE-7}")            #jump back to if
            appendCode("LOAD @TMP1")                # id = result
            appendCode("STORE @"+procName+"_"+identifier)

        elif exp[0] == "mod": # mod p d

            appendCode("SET 0")                         # result = 0
            appendCode("STORE @TMP1")
            appendCode("LOAD @"+exp2)    # if d = 0 jump_out
            appendCode("JZERO @")                       #jump out
            appendCode("LOAD @"+exp1)    # rest = p
            appendCode("STORE @TMP2")                   # acc = rest - d
            appendCode("SUB @"+exp2)
            appendCode("JZERO @")                       # if 0 jump_out 
            appendCode("STORE @TMP2")                   # rest = acc
            appendCode("SET 1")                         # result + 1
            appendCode("ADD @TMP1")
            appendCode("STORE @TMP1")
            appendCode("LOAD @TMP2")                    # acc = rest - d
            appendCode("SUB @"+exp2)
            appendCode("JUMP @{HERE-7}")                # jump back to if
            appendCode("LOAD @TMP2")                    # id = rest
            appendCode("STORE @"+procName+"_"+identifier)

        else:   #a:=b
            appendCode("LOAD @"+procName+"_"+exp[0])
            appendCode("STORE @"+procName+"_"+identifier)


    def translateAssignPROC(self,identifier,exp,procName):
        appendCode = self.code.append

        if exp[0].isnumeric(): #a:=5
            appendCode("SET "+exp[0])
            appendCode("STOREI @"+procName+"_"+identifier)

        elif exp[0] == "add":
            appendCode("LOADI @"+procName+"_"+exp[1])   # TODO if @"+procName+"_"+exp[1] / @"+exp1
            appendCode("ADDI @"+procName+"_"+exp[2])    # TODO if 
            appendCode("STOREI @"+procName+"_"+identifier)

        elif exp[0] == "sub":
            appendCode("LOADI @"+procName+"_"+exp[1])
            appendCode("SUBI @"+procName+"_"+exp[2])
            appendCode("STOREI @"+procName+"_"+identifier)

        elif exp[0] == "mul": # multi p q
            
            appendCode("SET 0")                             # acc = 0
            appendCode("STOREI @TMP2")                      # m = acc
            appendCode("LOADI @"+procName+"_"+exp[1])       # acc = p
                                                            # n = acc
                                                            # should it be a line?
                                                            # if acc = 0 break
            appendCode("JZERO @{HERE+9} [multi x 0, dont even try just return 0]")
            appendCode("SUBI @1")                           #   acc -1
            appendCode("STOREI @TMP1")                      #   n = acc
            appendCode("LOADI @TMP2")                       # 	acc = m
            appendCode("ADDI @"+procName+"_"+exp[2])        # 	acc + q
            appendCode("STOREI @TMP2")                      # 	m = acc
            appendCode("LOADI @TMP1")                       # 	acc = n
            appendCode("JZERO @{HERE-6}")                   # 	jump back if
            appendCode("LOADI @TMP2")                       # acc = m
            appendCode("STOREI @"+procName+"_"+identifier)  # id = acc

        elif exp[0] == "div":# div p d

            appendCode("SET 0")                             # result = 0
            appendCode("STOREI @TMP1")
            appendCode("LOADI @"+procName+"_"+exp[2])       # if d = 0 jump_out
            appendCode("JZERO @")                           # jump out
            appendCode("LOADI @"+procName+"_"+exp[1])       # rest = p
            appendCode("STOREI @TMP2")
            appendCode("SUBI @"+procName+"_"+exp[2])        # acc = rest - d
            appendCode("JZERO @")                           # if 0 jump_out
            appendCode("STOREI @TMP2")                      # rest = acc
            appendCode("SET 1")                             # result + 1
            appendCode("ADDI @TMP1")
            appendCode("STOREI @TMP1")
            appendCode("LOADI @TMP2")                       # acc = rest - d
            appendCode("SUBI @"+procName+"_"+exp[2])
            appendCode("JUMP @{HERE-7}")                    #jump back to if
            appendCode("LOADI @TMP1")                       # id = result
            appendCode("STOREI @"+procName+"_"+identifier)

        elif exp[0] == "mod": # mod p d

            appendCode("SET 0")                         # result = 0
            appendCode("STOREI @TMP1")
            appendCode("LOADI @"+procName+"_"+exp[2])   # if d = 0 jump_out
            appendCode("JZERO @")                       #jump out
            appendCode("LOADI @"+procName+"_"+exp[1])   # rest = p
            appendCode("STORE @TMP2")
            appendCode("SUBI @"+procName+"_"+exp[2])    # acc = rest - d
            appendCode("JZERO @")                       # if 0 jump_out
            appendCode("STOREI @TMP2")                  # rest = acc
            appendCode("SET 1")                         # result + 1
            appendCode("ADDI @TMP1")
            appendCode("STOREI @TMP1")
            appendCode("LOADI @TMP2")                   # acc = rest - d
            appendCode("SUBI @"+procName+"_"+exp[2])
            appendCode("JUMP @{HERE-7}")                #jump back to if
            appendCode("LOADI @TMP2")                   # id = rest
            appendCode("STOREI @"+procName+"_"+identifier)

        else:   #a:=b
            appendCode("LOADI @"+exp[0])
            appendCode("STOREI @"+procName+"_"+identifier)


    def translateConditionMAIN(self,cond,procName,codePointer,jumpF):
        appendCode = self.code.append

        if cond[1].isnumeric():
            cond1 = cond[1]
        else:
            cond1 = procName+"_"+cond[1]
        if cond[2].isnumeric():
            cond2 = cond[2]
        else:
            cond2 = procName+"_"+cond[2]

        if cond[0] == "eq":
                                                        # 2 3       # 3 2
            appendCode("SET 1 [$"+codePointer+"]")      # acc = 1   # acc = 1
            appendCode("ADD @"+cond1)    # acc = 2   # acc = 4
            appendCode("SUB @"+cond2)    # acc = 0   # acc = 2
            appendCode("JPOS @"+jumpF)                  # JUMP OUT  # nothing
            appendCode("SUB @1")                        #           # acc = 1
            appendCode("JPOS @"+jumpF)                  #           # JUMP OUT
            # appendCode("JUMP @"+jumpT)                #  True only on this line
            
        elif cond[0] == "ne":  # TODO set jumps
                                                        # 3 4           # 5 4
            appendCode("SET 1 [$"+codePointer+"]")      # acc = 1       # acc = 1
            appendCode("ADD @"+cond1)    # acc = 4       # acc = 6
            appendCode("SUB @"+cond2)    # acc = 0       # acc = 2
            appendCode("JZERO @"+jumpF)                 # NOT jump_out  # NO action
            appendCode("SUB @1")                        # acc = 0       # acc = 1
            appendCode("JPOS @"+jumpF)                  #               # NOT jump_out
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        elif cond[0] == "gt":   # 

            appendCode("LOAD @"+cond1+"  [$"+codePointer+"]")
            appendCode("SUB @"+cond2)
            appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)

        elif cond[0] == "ge":  # TODO set jumps

            appendCode("SET 1 [$"+codePointer+"]")
            appendCode("ADD @"+cond1)
            appendCode("SUB @"+cond2)
            appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        else:
            appendCode("ERROR "+cond)

    def translateConditionPROC(self,cond,procName,codePointer,jumpF): #TODO
        appendCode = self.code.append
        
        if cond[1].isnumeric():
            cond1 = cond[1]
        else:
            cond1 = procName+"_"+cond[1]
        if cond[2].isnumeric():
            cond2 = cond[2]
        else:
            cond2 = procName+"_"+cond[2]
        
        if cond[0] == "eq":
                                                        # 2 3       # 3 2
            appendCode("SET 1 [$"+codePointer+"]")      # acc = 1   # acc = 1
            appendCode("ADDI @"+cond1)   # acc = 2   # acc = 4
            appendCode("SUBI @"+cond2)   # acc = 0   # acc = 2
            appendCode("JPOS @"+jumpF)                  # JUMP OUT  # nothing
            appendCode("SUBI @1")                       #           # acc = 1
            appendCode("JPOS @"+jumpF)                  #           # JUMP OUT
            # appendCode("JUMP @"+jumpT)                #  True only on this line
            
        elif cond[0] == "ne":  # TODO set jumps
                                                        # 3 4           # 5 4
            appendCode("SET 1 [$"+codePointer+"]")      # acc = 1       # acc = 1
            appendCode("ADDI @"+cond1)   # acc = 4       # acc = 6
            appendCode("SUBI @"+cond2)   # acc = 0       # acc = 2
            appendCode("JZERO @"+jumpF)                 # NOT jump_out  # NO action
            appendCode("SUBI @1")                       # acc = 0       # acc = 1
            appendCode("JPOS @"+jumpF)                  #               # NOT jump_out
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        elif cond[0] == "gt":   # 

            appendCode("LOADI @"+cond1+"  [$"+codePointer+"]")
            appendCode("SUBI @"+cond2)
            appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)

        elif cond[0] == "ge":  # TODO set jumps

            appendCode("SET 1 [$"+codePointer+"]")
            appendCode("ADDI @"+cond1)
            appendCode("SUBI @"+cond2)
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

    def evalVariables(self):
        for line_Nr in range(len(self.code)):
        # for instr in self.code:
            for i in range(len(tobiqContext_.variablesNames)):
            # for var in tobiqContext_.variablesNames:
                if "@"+tobiqContext_.variablesNames[i] in self.code[line_Nr]:
                    # print(tobiqContext_.variablesNames[i]+">"+str(i))
                    # print(self.code[line_Nr])
                    self.code[line_Nr] = self.code[line_Nr].replace("@"+tobiqContext_.variablesNames[i],str(i))
                    # print(self.code[line_Nr])