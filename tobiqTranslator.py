import tobiqContext_ as global_


class TobiqTranslator:
    code = []
    callbackTable = []

    def appendCode(self,instr):
        self.code.append(instr)
        global_.lineCounter=global_.lineCounter+1

    def translate(self):

        self.appendCode("JUMP @MAIN")

        self.translateProcedures()
        self.appendCode("HALT")

        self.evalVariables()
        self.evalJumps()

        return self.code

    def translateProcedures(self):
        for proc in global_.instructions:
            if proc[0] == "PROCEDURE":
                self.callbackTable.append([proc[1], global_.lineCounter])
                procNameVariables = self.getVarNameInProc(proc[1])
                self.translateBlock(proc[2],proc[1],procNameVariables)
            elif proc[0] == "MAIN":
                self.callbackTable.append(["MAIN", global_.lineCounter])
                procNameVariables = self.getVarNameInProc("MAIN")
                self.translateBlock(proc[1],"MAIN",procNameVariables)


    def translateBlock(self, block, procName,procNameVariables):
          # appendCode = self.code.append
        for inst in block:
            if inst[0] == "ASSIGN":
                if procName=="MAIN":
                    self.translateAssignMAIN(inst[1],inst[2],procName)
                else:
                    self.translateAssignPROC(inst[1],inst[2],procName)

            elif inst[0] == "IFELSE":
                tmpPointerFalse = "IFELSE+"+len(self.callbackTable)
                tmpPointerTrue = "IFELSE+"+len(self.callbackTable)
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"IFELSE",tmpPointerFalse)
                # else:
                #     self.translateConditionPROC(inst[1],inst[2],procName)
                self.translateBlock(inst[2],procName,procNameVariables)
                self.appendCode("JUMP @"+tmpPointerTrue+"    ["+tmpPointerFalse+"]")
                self.translateBlock(inst[3],procName,procNameVariables)
                self.code[-1]+=("  ["+tmpPointerTrue+"]")

            elif inst[0] == "IF":
                tmpPointer = "IF+"+len(self.callbackTable)
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"IF",tmpPointer)
                # else:
                #     self.translateConditionPROC(inst[1],inst[2],procName)
                self.translateBlock(inst[2],procName,procNameVariables)
                
                self.code[-1]+="  ["+tmpPointer+"]" #TODO check

            elif inst[0] == "WHILE":
                tmpPointer = "WHILE+"+len(self.callbackTable)
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"$HERE_While",tmpPointer)
                # else:
                #     self.translateConditionPROC(inst[1],inst[2],procName)
                self.translateBlock(inst[2],procName,procNameVariables)
                self.appendCode("JUMP @HERE_While    ["+tmpPointer+"]") #TODO

            elif inst[0] == "REPEAT":
                tmpPointerBack = "REPEAT_BACK+"+len(self.callbackTable)
                tmpPointerOut = "REPEAT_OUT+"+len(self.callbackTable)
                self.code[-1]+="  [$"+tmpPointerBack+"]"
                self.translateBlock(inst[2],procName,procNameVariables)
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1],procName,"Until",tmpPointerOut)
                # else:
                #     self.translateConditionPROC(inst[1],inst[2],procName)
                self.appendCode("JUMP @"+tmpPointerBack)
            
            elif inst[0] == "PROC": # DONE (hope so)
                for i in range(len(inst[2])):
                    self.appendCode("SET @"+procName+"_"+inst[2][i])
                    self.appendCode("STORE @"+procNameVariables[i])
                self.appendCode("SET "+str(global_.lineCounter+2)+" [JUMP_BACK PROC]")
                self.appendCode("STORE @"+procName+"_JUMPBACK")
                self.appendCode("JUMP @"+procName)
            
            elif inst[0] == "READ": 
                if procName=="MAIN":
                    self.appendCode("GET @"+procName+"_"+inst[1])
                else:
                    self.appendCode("GET @"+procName+"_"+inst[1])#TODO if not in main

            elif inst[0] == "WRITE":
                if procName=="MAIN":
                    self.appendCode("PUT @"+procName+"_"+inst[1])
                else:
                    self.appendCode("LOADI @"+procName+"_"+inst[1])
                    self.appendCode("PUT 0")

            else:
                print("ERROR "+inst)


    def translateAssignMAIN(self,identifier,exp,procName):
          # appendCode = self.code.append

        if exp[1].isnumeric():
            exp1 = exp[1]
        else:
            exp1 = procName+"_"+exp[1]
        if exp[2].isnumeric():
            exp2 = exp[2]
        else:
            exp2 = procName+"_"+exp[2]


        if exp[0].isnumeric(): #a:=5
            self.appendCode("SET "+exp[0])
            self.appendCode("STORE @"+procName+"_"+identifier)

        elif exp[0] == "add": 
            self.appendCode("LOAD @"+exp1)
            self.appendCode("ADD @"+exp2)
            self.appendCode("STORE @"+procName+"_"+identifier)

        elif exp[0] == "sub":
            self.appendCode("LOAD @"+exp1)
            self.appendCode("SUB @"+exp2)
            self.appendCode("STORE @"+procName+"_"+identifier)

        elif exp[0] == "mul": # multi p q
            
            self.appendCode("SET 0               [MULTI BEGIN]") # acc = 0
            self.appendCode("STORE @TMP2")                       # m = acc
            self.appendCode("LOAD @"+exp1)        # acc = p
                                                            # n = acc
                                                            # should it be a line?
            self.appendCode("JZERO @{HERE+9} [multi x 0, dont even try just return 0]") # if acc = 0 break
            self.appendCode("SUB @1")                            # acc -1
            self.appendCode("STORE @TMP1")                       # n = acc
            self.appendCode("LOAD @TMP2")                        # acc = m
            self.appendCode("ADD  @"+exp2)        # acc + q
            self.appendCode("STORE @TMP2")                       # m = acc
            self.appendCode("LOAD @TMP1")                        # acc = n
            self.appendCode("JZERO @{HERE-6}")                   # jump back if
            self.appendCode("LOAD @TMP2")                        # acc = m
            self.appendCode("STORE @"+procName+"_"+identifier+"[MULTI END]")  # id = acc

        elif exp[0] == "div":# div p d

            self.appendCode("SET 0")                     # result = 0
            self.appendCode("STORE @TMP1")
            self.appendCode("LOAD @"+exp2)# if d = 0 jump_out
            self.appendCode("JZERO @")                   #jump out
            self.appendCode("LOAD @"+exp1)# rest = p
            self.appendCode("STORE @TMP2")
            self.appendCode("SUB @"+exp2) # acc = rest - d
            self.appendCode("JZERO @")                   # if 0 jump_out
            self.appendCode("STORE @TMP2")               # rest = acc
            self.appendCode("SET 1")                     # result + 1
            self.appendCode("ADD @TMP1")
            self.appendCode("STORE @TMP1")               # acc = rest - d
            self.appendCode("LOAD @TMP2")
            self.appendCode("SUB @"+exp2)
            self.appendCode("JUMP "+str(global_.lineCounter-7))            #jump back to if
            self.appendCode("LOAD @TMP1")                # id = result
            self.appendCode("STORE @"+procName+"_"+identifier)

        elif exp[0] == "mod": # mod p d

            self.appendCode("SET 0")                         # result = 0
            self.appendCode("STORE @TMP1")
            self.appendCode("LOAD @"+exp2)    # if d = 0 jump_out
            self.appendCode("JZERO @")                       #jump out
            self.appendCode("LOAD @"+exp1)    # rest = p
            self.appendCode("STORE @TMP2")                   # acc = rest - d
            self.appendCode("SUB @"+exp2)
            self.appendCode("JZERO @")                       # if 0 jump_out 
            self.appendCode("STORE @TMP2")                   # rest = acc
            self.appendCode("SET 1")                         # result + 1
            self.appendCode("ADD @TMP1")
            self.appendCode("STORE @TMP1")
            self.appendCode("LOAD @TMP2")                    # acc = rest - d
            self.appendCode("SUB @"+exp2)
            self.appendCode("JUMP "+str(global_.lineCounter-7))                # jump back to if
            self.appendCode("LOAD @TMP2")                    # id = rest
            self.appendCode("STORE @"+procName+"_"+identifier)

        else:   #a:=b
            self.appendCode("LOAD @"+procName+"_"+exp[0])
            self.appendCode("STORE @"+procName+"_"+identifier)


    def translateAssignPROC(self,identifier,exp,procName):
          # appendCode = self.code.append

        if exp[0].isnumeric(): #a:=5
            self.appendCode("SET "+exp[0])
            self.appendCode("STOREI @"+procName+"_"+identifier)

        elif exp[0] == "add":
            self.appendCode("LOADI @"+procName+"_"+exp[1])   # TODO if @"+procName+"_"+exp[1] / @"+exp1
            self.appendCode("ADDI @"+procName+"_"+exp[2])    # TODO if 
            self.appendCode("STOREI @"+procName+"_"+identifier)

        elif exp[0] == "sub":
            self.appendCode("LOADI @"+procName+"_"+exp[1])
            self.appendCode("SUBI @"+procName+"_"+exp[2])
            self.appendCode("STOREI @"+procName+"_"+identifier)

        elif exp[0] == "mul": # multi p q
            
            self.appendCode("SET 0")                             # acc = 0
            self.appendCode("STOREI @TMP2")                      # m = acc
            self.appendCode("LOADI @"+procName+"_"+exp[1])       # acc = p
                                                            # n = acc
                                                            # should it be a line?
                                                            # if acc = 0 break
            self.appendCode("JZERO @{HERE+9} [multi x 0, dont even try just return 0]")
            self.appendCode("SUBI @1")                           #   acc -1
            self.appendCode("STOREI @TMP1")                      #   n = acc
            self.appendCode("LOADI @TMP2")                       # 	acc = m
            self.appendCode("ADDI @"+procName+"_"+exp[2])        # 	acc + q
            self.appendCode("STOREI @TMP2")                      # 	m = acc
            self.appendCode("LOADI @TMP1")                       # 	acc = n
            self.appendCode("JZERO @{HERE-6}")                   # 	jump back if
            self.appendCode("LOADI @TMP2")                       # acc = m
            self.appendCode("STOREI @"+procName+"_"+identifier)  # id = acc

        elif exp[0] == "div":# div p d

            self.appendCode("SET 0")                             # result = 0
            self.appendCode("STOREI @TMP1")
            self.appendCode("LOADI @"+procName+"_"+exp[2])       # if d = 0 jump_out
            self.appendCode("JZERO @")                           # jump out
            self.appendCode("LOADI @"+procName+"_"+exp[1])       # rest = p
            self.appendCode("STOREI @TMP2")
            self.appendCode("SUBI @"+procName+"_"+exp[2])        # acc = rest - d
            self.appendCode("JZERO @")                           # if 0 jump_out
            self.appendCode("STOREI @TMP2")                      # rest = acc
            self.appendCode("SET 1")                             # result + 1
            self.appendCode("ADDI @TMP1")
            self.appendCode("STOREI @TMP1")
            self.appendCode("LOADI @TMP2")                       # acc = rest - d
            self.appendCode("SUBI @"+procName+"_"+exp[2])
            self.appendCode("JUMP "+str(global_.lineCounter-7))                    #jump back to if
            self.appendCode("LOADI @TMP1")                       # id = result
            self.appendCode("STOREI @"+procName+"_"+identifier)

        elif exp[0] == "mod": # mod p d

            self.appendCode("SET 0")                         # result = 0
            self.appendCode("STOREI @TMP1")
            self.appendCode("LOADI @"+procName+"_"+exp[2])   # if d = 0 jump_out
            self.appendCode("JZERO @")                       #jump out
            self.appendCode("LOADI @"+procName+"_"+exp[1])   # rest = p
            self.appendCode("STORE @TMP2")
            self.appendCode("SUBI @"+procName+"_"+exp[2])    # acc = rest - d
            self.appendCode("JZERO @")                       # if 0 jump_out
            self.appendCode("STOREI @TMP2")                  # rest = acc
            self.appendCode("SET 1")                         # result + 1
            self.appendCode("ADDI @TMP1")
            self.appendCode("STOREI @TMP1")
            self.appendCode("LOADI @TMP2")                   # acc = rest - d
            self.appendCode("SUBI @"+procName+"_"+exp[2])
            self.appendCode("JUMP "+str(global_.lineCounter-7))                #jump back to if
            self.appendCode("LOADI @TMP2")                   # id = rest
            self.appendCode("STOREI @"+procName+"_"+identifier)

        else:   #a:=b
            self.appendCode("LOADI @"+exp[0])
            self.appendCode("STOREI @"+procName+"_"+identifier)


    def translateConditionMAIN(self,cond,procName,codePointer,jumpF):
          # appendCode = self.code.append

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
            self.appendCode("SET 1 [$"+codePointer+"]")      # acc = 1   # acc = 1
            self.appendCode("ADD @"+cond1)    # acc = 2   # acc = 4
            self.appendCode("SUB @"+cond2)    # acc = 0   # acc = 2
            self.appendCode("JPOS @"+jumpF)                  # JUMP OUT  # nothing
            self.appendCode("SUB @1")                        #           # acc = 1
            self.appendCode("JPOS @"+jumpF)                  #           # JUMP OUT
            # appendCode("JUMP @"+jumpT)                #  True only on this line
            
        elif cond[0] == "ne":  # TODO set jumps
                                                        # 3 4           # 5 4
            self.appendCode("SET 1 [$"+codePointer+"]")      # acc = 1       # acc = 1
            self.appendCode("ADD @"+cond1)    # acc = 4       # acc = 6
            self.appendCode("SUB @"+cond2)    # acc = 0       # acc = 2
            self.appendCode("JZERO @"+jumpF)                 # NOT jump_out  # NO action
            self.appendCode("SUB @1")                        # acc = 0       # acc = 1
            self.appendCode("JPOS @"+jumpF)                  #               # NOT jump_out
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        elif cond[0] == "gt":   # 

            self.appendCode("LOAD @"+cond1+"  [$"+codePointer+"]")
            self.appendCode("SUB @"+cond2)
            self.appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)

        elif cond[0] == "ge":  # TODO set jumps

            self.appendCode("SET 1 [$"+codePointer+"]")
            self.appendCode("ADD @"+cond1)
            self.appendCode("SUB @"+cond2)
            self.appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        else:
            self.appendCode("ERROR "+cond)

    def translateConditionPROC(self,cond,procName,codePointer,jumpF): #TODO
          # appendCode = self.code.append
        
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
            self.appendCode("SET 1 [$"+codePointer+"]")      # acc = 1   # acc = 1
            self.appendCode("ADDI @"+cond1)   # acc = 2   # acc = 4
            self.appendCode("SUBI @"+cond2)   # acc = 0   # acc = 2
            self.appendCode("JPOS @"+jumpF)                  # JUMP OUT  # nothing
            self.appendCode("SUBI @1")                       #           # acc = 1
            self.appendCode("JPOS @"+jumpF)                  #           # JUMP OUT
            # appendCode("JUMP @"+jumpT)                #  True only on this line
            
        elif cond[0] == "ne":  # TODO set jumps
                                                        # 3 4           # 5 4
            self.appendCode("SET 1 [$"+codePointer+"]")      # acc = 1       # acc = 1
            self.appendCode("ADDI @"+cond1)   # acc = 4       # acc = 6
            self.appendCode("SUBI @"+cond2)   # acc = 0       # acc = 2
            self.appendCode("JZERO @"+jumpF)                 # NOT jump_out  # NO action
            self.appendCode("SUBI @1")                       # acc = 0       # acc = 1
            self.appendCode("JPOS @"+jumpF)                  #               # NOT jump_out
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        elif cond[0] == "gt":   # 

            self.appendCode("LOADI @"+cond1+"  [$"+codePointer+"]")
            self.appendCode("SUBI @"+cond2)
            self.appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)

        elif cond[0] == "ge":  # TODO set jumps

            self.appendCode("SET 1 [$"+codePointer+"]")
            self.appendCode("ADDI @"+cond1)
            self.appendCode("SUBI @"+cond2)
            self.appendCode("JPOS @"+jumpF)
            # appendCode("JUMP @"+jumpT)
            # appendCode(cond)
        else:
            self.appendCode("ERROR "+cond)


    def getVarNameInProc(self,procName):
        result=[]
        for var in global_.variablesNames:
            if var.startswith(procName):
                result.append(var)
        return result

    def evalVariables(self):
        for line_Nr in range(len(self.code)):
        # for instr in self.code:
            for var_Nr in range(len(global_.variablesNames)):
            # for var in global_.variablesNames:
                if "@"+global_.variablesNames[var_Nr] in self.code[line_Nr]:
                    # print(global_.variablesNames[i]+">"+str(i))
                    # print(self.code[line_Nr])
                    self.code[line_Nr] = self.code[line_Nr].replace("@"+global_.variablesNames[var_Nr],str(var_Nr))
                    # print(self.code[line_Nr])

    def evalJumps(self):
        for line_Nr in range(len(self.code)):
            for jump_Nr in range(len(self.callbackTable)):
            # for var in global_.variablesNames:
                if "@"+self.callbackTable[jump_Nr][0] in self.code[line_Nr]:
                    #  and\
                    # self.callbackTable[jump_Nr][1] != null:
                    # print(global_.variablesNames[i]+">"+str(i))
                    # print(self.code[line_Nr])
                    self.code[line_Nr] = self.code[line_Nr].replace(
                        "@"+self.callbackTable[jump_Nr][0],
                        str(self.callbackTable[jump_Nr][1]))
                    # print(self.code[line_Nr])