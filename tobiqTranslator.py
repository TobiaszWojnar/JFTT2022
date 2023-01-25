import tobiqContext_ as global_


class TobiqTranslator:
    code = []
    callbackTable = []

    def appendCode(self,instr):
        self.code.append(instr)
        global_.lineCounter=global_.lineCounter+1

    def translate(self):

        

        self.appendCode("JUMP @MAIN_JUMP")

        self.translateProcedures()
        self.appendCode("HALT")

        self.evalVariables()
        self.evalJumps()

        print("###################")
        print(self.callbackTable)

        return self.code

    def translateProcedures(self):
        for proc in global_.instructions:
            if proc[0] == "PROCEDURE":
                self.callbackTable.append([proc[1], global_.lineCounter])
                procNameVariables = self.getVarNameInProc(proc[1])
                # TODO ADD JUMPI back ###########################################################################
                self.translateBlock(proc[2], proc[1], procNameVariables)
            elif proc[0] == "MAIN":
                self.callbackTable.append(["MAIN_JUMP", global_.lineCounter])
                procNameVariables = self.getVarNameInProc("MAIN")
                self.translateBlock(proc[1],"MAIN", procNameVariables)


    def translateBlock(self, block, procName, procNameVariables):

        for inst in block:
            if inst[0] == "ASSIGN":
                if procName=="MAIN":
                    self.translateAssignMAIN(inst[1],inst[2], procName)
                else:
                    self.translateAssignPROC(inst[1],inst[2], procName)

            elif inst[0] == "IFELSE":

                ifPointerFalse = "IFELSE_F_"+str(len(self.callbackTable))
                self.callbackTable.append([ifPointerFalse, 0])
                ifPointerTrue = "IFELSE_T_"+str(len(self.callbackTable))
                self.callbackTable.append([ifPointerTrue, 0])


                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1], procName,"IFELSE+",ifPointerFalse)
                else:
                    self.translateConditionPROC(inst[1], procName,"IFELSE+",ifPointerFalse)
                self.translateBlock(inst[2], procName, procNameVariables)
                self.appendCode("JUMP @"+ifPointerTrue)
                # SET FALSE
                # Setting value of the jump
                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == ifPointerFalse[0]:
                        self.callbackTable[jumpNr][1] = global_.lineCounter

                self.translateBlock(inst[3], procName, procNameVariables)

                # SET TRUE
                # Setting value of the jump
                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == ifPointerTrue[0]:
                        self.callbackTable[jumpNr][1] = global_.lineCounter

            elif inst[0] == "IF":

                # Declaring pointer to jump
                ifPointerFalse = "IF_F_"+str(len(self.callbackTable))
                self.callbackTable.append([ifPointerFalse, 0])

                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1], procName,"IF+",ifPointerFalse)
                else:
                    self.translateConditionPROC(inst[1], procName,"IF+",ifPointerFalse)
                self.translateBlock(inst[2], procName, procNameVariables)
                

                # Setting value of the jump
                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == ifPointerFalse[0]:
                        self.callbackTable[jumpNr][1] = global_.lineCounter

            elif inst[0] == "WHILE":
                whilePointerFalse = "WHILE_F_"+str(len(self.callbackTable))
                self.callbackTable.append([whilePointerFalse, 0])
                whilePointerTrue = "WHILE_T_"+str(len(self.callbackTable))
                self.callbackTable.append([whilePointerTrue, 0])

                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1], procName, whilePointerTrue, whilePointerFalse)
                else:
                    self.translateConditionPROC(inst[1], procName, whilePointerTrue, whilePointerFalse)
                self.translateBlock(inst[2], procName, procNameVariables)
                self.appendCode("JUMP @"+whilePointerTrue)

                # Setting value of the jump
                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == whilePointerFalse[0]:
                        self.callbackTable[jumpNr][1] = global_.lineCounter

            elif inst[0] == "REPEAT":
                repeatPointerBack = "REPEAT_BACK_"+str(len(self.callbackTable))
                self.callbackTable.append([repeatPointerBack, global_.lineCounter])
                repeatPointerOut = "REPEAT_OUT_"+str(len(self.callbackTable))
                self.callbackTable.append([repeatPointerOut, 0])

                self.translateBlock(inst[2], procName, procNameVariables)
                if procName=="MAIN":
                    self.translateConditionMAIN(inst[1], procName,"UNTIL",repeatPointerOut)
                else:
                    self.translateConditionPROC(inst[1], procName,"UNTIL",repeatPointerOut)
                self.appendCode("JUMP @"+repeatPointerBack)

                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == repeatPointerOut[0]:
                        self.callbackTable[jumpNr][1] = global_.lineCounter
            
            elif inst[0] == "PROC": # DONE (hope so)
                for i in range(len(inst[2])):
                    self.appendCode("SET @"+procName+"_"+inst[2][i])
                    self.appendCode("STORE @"+procNameVariables[i])
                self.appendCode("SET "+str(global_.lineCounter+2)+" [JUMP_BACK PROC]")
                self.appendCode("STORE @"+inst[1]+"_JUMPBACK")
                self.appendCode("JUMP @"+inst[1])

            elif inst[0] == "READ": 
                if procName=="MAIN":
                    self.appendCode("GET @"+procName+"_"+inst[1])
                else:
                    self.appendCode("GET @"+procName+"_"+inst[1])#TODO if not in main

            elif inst[0] == "WRITE":

                if inst[1].isnumeric():
                    valToWrite = inst[1]
                else:
                    valToWrite = procName+"_"+inst[1]


                if procName=="MAIN":
                    self.appendCode("PUT @"+valToWrite+ " [test2]")
                else:
                    self.appendCode("LOADI @"+valToWrite)
                    self.appendCode("PUT 0 [test1]")

            else:
                print("ERROR "+inst)


    def translateAssignMAIN(self,identifier,exp, procName):

        if isinstance(exp, int):
            self.appendCode("SET "+exp)
            self.appendCode("STORE @"+procName+"_"+identifier)

        elif isinstance(exp, str):
            self.appendCode("LOAD @"+procName+"_"+exp)
            self.appendCode("STORE @"+procName+"_"+identifier)

        elif isinstance(exp, list):
            exp1 = exp[1] if exp[1].isnumeric() else procName+"_"+exp[1]
            exp2 = exp[2] if exp[2].isnumeric() else procName+"_"+exp[2]

            if exp[0] == "add": 
                self.appendCode("LOAD @"+exp1)
                self.appendCode("ADD @"+exp2)
                self.appendCode("STORE @"+procName+"_"+identifier)

            elif exp[0] == "sub":
                self.appendCode("LOAD @"+exp1)
                self.appendCode("SUB @"+exp2)
                self.appendCode("STORE @"+procName+"_"+identifier)

            elif exp[0] == "mul": # multi p q
                
                self.appendCode("SET 0               [MULTI BEGIN]")    # acc = 0
                self.appendCode("STORE @TMP2")                          # m = acc
                self.appendCode("LOAD @"+exp1)                          # acc = p
                                                                        # n = acc
                                                                        # should it be a line?
                self.appendCode("JZERO "+str(global_.lineCounter+9))    # if acc = 0 break
                self.appendCode("SUB @1")                               # acc -1
                self.appendCode("STORE @TMP1")                          # n = acc
                self.appendCode("LOAD @TMP2")                           # acc = m
                self.appendCode("ADD  @"+exp2)                          # acc + q
                self.appendCode("STORE @TMP2")                          # m = acc
                self.appendCode("LOAD @TMP1")                           # acc = n
                self.appendCode("JZERO "+str(global_.lineCounter-6))    # jump back if
                self.appendCode("LOAD @TMP2")                           # acc = m
                self.appendCode("STORE @"+procName+"_"+identifier+" [MULTI END]")  # id = acc

            elif exp[0] == "div":# div p d

                self.appendCode("SET 0")                            # result = 0
                self.appendCode("STORE @TMP1")
                self.appendCode("LOAD @"+exp2)                      # if d = 0 jump_out
                self.appendCode("JZERO "+str(global_.lineCounter+13)) #jump out
                self.appendCode("LOAD @"+exp1)                      # rest = p
                self.appendCode("STORE @TMP2")
                self.appendCode("SUB @"+exp2)                       # acc = rest - d
                self.appendCode("JZERO "+str(global_.lineCounter+9)) # if 0 jump_out
                self.appendCode("STORE @TMP2")                      # rest = acc
                self.appendCode("SET 1")                            # result + 1
                self.appendCode("ADD @TMP1")
                self.appendCode("STORE @TMP1")                      # acc = rest - d
                self.appendCode("LOAD @TMP2")
                self.appendCode("SUB @"+exp2)
                self.appendCode("JUMP "+str(global_.lineCounter-7)) #jump back to if
                self.appendCode("LOAD @TMP1")                   # id = result
                self.appendCode("STORE @"+procName+"_"+identifier)

            elif exp[0] == "mod": # mod p d

                self.appendCode("SET 0")                            # result = 0
                self.appendCode("STORE @TMP1")
                self.appendCode("LOAD @"+exp2)                      # if d = 0 jump_out
                self.appendCode("JZERO "+str(global_.lineCounter+13)) #jump out
                self.appendCode("LOAD @"+exp1)                      # rest = p
                self.appendCode("STORE @TMP2")
                self.appendCode("SUB @"+exp2)                       # acc = rest - d
                self.appendCode("JZERO "+str(global_.lineCounter+9)) # if 0 jump_out
                self.appendCode("STORE @TMP2")                      # rest = acc
                self.appendCode("SET 1")                            # result + 1
                self.appendCode("ADD @TMP1")
                self.appendCode("STORE @TMP1")                      # acc = rest - d
                self.appendCode("LOAD @TMP2")
                self.appendCode("SUB @"+exp2)
                self.appendCode("JUMP "+str(global_.lineCounter-7)) #jump back to if
                self.appendCode("LOAD @TMP2")                       # id = rest
                self.appendCode("STORE @"+procName+"_"+identifier)

            else:
                print("ERROR undefined exp"+str(exp))
        else:
            print("ERROR exp wrong type"+str(exp))


    def translateAssignPROC(self,identifier,exp, procName):

        if isinstance(exp, int):
            self.appendCode("SET "+exp)
            self.appendCode("STOREI @"+procName+"_"+identifier)
        elif isinstance(exp, str):
            self.appendCode("LOADI @"+procName+"_"+exp)
            self.appendCode("STOREI @"+procName+"_"+identifier)
        elif isinstance(exp, list):
            exp1 = exp[1] if exp[1].isnumeric() else procName+"_"+exp[1]
            exp2 = exp[2] if exp[2].isnumeric() else procName+"_"+exp[2]

            if exp[0] == "add":
                self.appendCode("LOADI @"+exp1)
                self.appendCode("ADDI @"+exp2)
                self.appendCode("STOREI @"+procName+"_"+identifier)

            elif exp[0] == "sub":
                self.appendCode("LOADI @"+exp1)
                self.appendCode("SUBI @"+exp2)
                self.appendCode("STOREI @"+procName+"_"+identifier)

            elif exp[0] == "mul": # multi p q
                
                self.appendCode("SET 0")                             # acc = 0
                self.appendCode("STOREI @TMP2")                      # m = acc
                self.appendCode("LOADI @"+exp1)       # acc = p
                                                                    # n = acc
                                                                    # should it be a line?
                                                                    # if acc = 0 break
                self.appendCode("JZERO "+str(global_.lineCounter+9)+" [multi x 0, dont even try just return 0]")
                self.appendCode("SUBI @1")                           #   acc -1
                self.appendCode("STOREI @TMP1")                      #   n = acc
                self.appendCode("LOADI @TMP2")                       # 	acc = m
                self.appendCode("ADDI @"+exp2)        # 	acc + q
                self.appendCode("STOREI @TMP2")                      # 	m = acc
                self.appendCode("LOADI @TMP1")                       # 	acc = n
                self.appendCode("JZERO "+str(global_.lineCounter-6))                   # 	jump back if
                self.appendCode("LOADI @TMP2")                       # acc = m
                self.appendCode("STOREI @"+procName+"_"+identifier)  # id = acc

            elif exp[0] == "div":# div p d

                self.appendCode("SET 0")                             # result = 0
                self.appendCode("STOREI @TMP1")
                self.appendCode("LOADI @"+exp2)                      # if d = 0 jump_out
                self.appendCode("JZERO "+str(global_.lineCounter+13))# jump out
                self.appendCode("LOADI @"+exp1)                      # rest = p
                self.appendCode("STOREI @TMP2")
                self.appendCode("SUBI @"+exp2)                       # acc = rest - d
                self.appendCode("JZERO "+str(global_.lineCounter+9)) # if 0 jump_out
                self.appendCode("STOREI @TMP2")                      # rest = acc
                self.appendCode("SET 1")                             # result + 1
                self.appendCode("ADDI @TMP1")
                self.appendCode("STOREI @TMP1")
                self.appendCode("LOADI @TMP2")                        # acc = rest - d
                self.appendCode("SUBI @"+exp2)
                self.appendCode("JUMP "+str(global_.lineCounter-7))   #jump back to if
                self.appendCode("LOADI @TMP1")                        # id = result
                self.appendCode("STOREI @"+procName+"_"+identifier)

            elif exp[0] == "mod": # mod p d

                self.appendCode("SET 0")                             # result = 0
                self.appendCode("STOREI @TMP1")
                self.appendCode("LOADI @"+exp2)                      # if d = 0 jump_out
                self.appendCode("JZERO "+str(global_.lineCounter+13))# jump out
                self.appendCode("LOADI @"+exp1)                      # rest = p
                self.appendCode("STOREI @TMP2")
                self.appendCode("SUBI @"+exp2)                       # acc = rest - d
                self.appendCode("JZERO "+str(global_.lineCounter+9)) # if 0 jump_out
                self.appendCode("STOREI @TMP2")                      # rest = acc
                self.appendCode("SET 1")                             # result + 1
                self.appendCode("ADDI @TMP1")
                self.appendCode("STOREI @TMP1")
                self.appendCode("LOADI @TMP2")                       # acc = rest - d
                self.appendCode("SUBI @"+exp2)
                self.appendCode("JUMP "+str(global_.lineCounter-7))  #jump back to if
                self.appendCode("LOADI @TMP2")                       # id = rest
                self.appendCode("STOREI @"+procName+"_"+identifier)

            else:
                print("ERROR undefined exp"+str(exp))
        else:
            print("ERROR exp wrong type"+str(exp))


    def translateConditionMAIN(self,cond, procName,codePointer,jumpF):

        # Fix that some values are constants
        cond1 = cond[1] if cond[1].isnumeric() else procName+"_"+cond[1]
        cond2 = cond[2] if cond[2].isnumeric() else procName+"_"+cond[2]        

        self.callbackTable.append([codePointer, global_.lineCounter])

        if cond[0] == "eq":
                                                            # 2 3       # 3 2
            self.appendCode("SET 1")                        # acc = 1   # acc = 1
            self.appendCode("ADD @"+cond1)                  # acc = 2   # acc = 4
            self.appendCode("SUB @"+cond2)                  # acc = 0   # acc = 2
            self.appendCode("JPOS @"+jumpF)                 # JUMP OUT  # nothing
            self.appendCode("SUB @1")                       #           # acc = 1
            self.appendCode("JPOS @"+jumpF)                 #           # JUMP OUT
            
        elif cond[0] == "ne":
                                                            # 3 4           # 5 4
            self.appendCode("SET 1")                        # acc = 1       # acc = 1
            self.appendCode("ADD @"+cond1)                  # acc = 4       # acc = 6
            self.appendCode("SUB @"+cond2)                  # acc = 0       # acc = 2
            self.appendCode("JZERO @"+jumpF)                # NOT jump_out  # NO action
            self.appendCode("SUB @1")                       # acc = 0       # acc = 1
            self.appendCode("JPOS @"+jumpF)                 #               # NOT jump_out
            
        elif cond[0] == "gt":   # 

            self.appendCode("LOAD @"+cond1)
            self.appendCode("SUB @"+cond2)
            self.appendCode("JPOS @"+jumpF)

        elif cond[0] == "ge":

            self.appendCode("SET 1")
            self.appendCode("ADD @"+cond1)
            self.appendCode("SUB @"+cond2)
            self.appendCode("JPOS @"+jumpF)
            
        else:
            self.appendCode("ERROR "+cond)

    def translateConditionPROC(self,cond, procName,codePointer,jumpF):
        
        # Fix that some values are constants
        cond1 = cond[1] if cond[1].isnumeric() else procName+"_"+cond[1]
        cond2 = cond[2] if cond[2].isnumeric() else procName+"_"+cond[2]     

        self.callbackTable.append([codePointer, global_.lineCounter])
        
        if cond[0] == "eq":
                                                             # 2 3       # 3 2
            self.appendCode("SET 1")                         # acc = 1   # acc = 1
            self.appendCode("ADDI @"+cond1)                  # acc = 2   # acc = 4
            self.appendCode("SUBI @"+cond2)                  # acc = 0   # acc = 2
            self.appendCode("JPOS @"+jumpF)                  # JUMP OUT  # nothing
            self.appendCode("SUBI @1")                       #           # acc = 1
            self.appendCode("JPOS @"+jumpF)                  #           # JUMP OUT
            
        elif cond[0] == "ne":
                                                             # 3 4           # 5 4
            self.appendCode("SET 1")                         # acc = 1       # acc = 1
            self.appendCode("ADDI @"+cond1)                  # acc = 4       # acc = 6
            self.appendCode("SUBI @"+cond2)                  # acc = 0       # acc = 2
            self.appendCode("JZERO @"+jumpF)                 # NOT jump_out  # NO action
            self.appendCode("SUBI @1")                       # acc = 0       # acc = 1
            self.appendCode("JPOS @"+jumpF)                  #               # NOT jump_out
            
        elif cond[0] == "gt":   # 

            self.appendCode("LOADI @"+cond1)
            self.appendCode("SUBI @"+cond2)
            self.appendCode("JPOS @"+jumpF)

        elif cond[0] == "ge":

            self.appendCode("SET 1")
            self.appendCode("ADDI @"+cond1)
            self.appendCode("SUBI @"+cond2)
            self.appendCode("JPOS @"+jumpF)
            
        else:
            self.appendCode("ERROR "+cond)


    def getVarNameInProc(self, procName):
        result=[]
        for var in global_.variablesNames:
            if var.startswith(procName):
                result.append(var)
        return result



    def evalVariables(self):
            for lineNr, lineVal in enumerate(self.code):
                for varNr, varVal in enumerate(global_.variablesNames):
                    if "@"+varVal in lineVal:
                        self.code[lineNr] = lineVal.replace("@"+varVal,str(varNr))


    def evalJumps(self):
        for lineNr, lineVal in enumerate(self.code):
            for jumpVal in reversed(self.callbackTable):
                if "@"+jumpVal[0] in lineVal:
                    self.code[lineNr] = lineVal.replace("@"+jumpVal[0], str(jumpVal[1]))