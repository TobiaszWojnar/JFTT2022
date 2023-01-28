import tobiqContext_ as global_


class TobiqTranslator:
    code = []
    callbackTable = []
    comments = ""

    def translate(self):

        self.setupConstants()

        self.appendCode("JUMP @MAIN_JUMP    [Jump to main]")

        self.translateProcedures()
        self.appendCode("HALT")

        self.evalVariables()
        self.evalJumps()

        print("######### callbackTable ##########")
        print(self.callbackTable)

        return self.code

    def appendCode(self,instr):
        self.comments = self.comments.replace("[", "(" ).replace("]", ")" )

        global_.lineCounter=global_.lineCounter+1
        if self.comments != "":
            self.code.append(instr+"    ["+self.comments+"]")
            self.comments = ""
        else:
            self.code.append(instr)


    def setupConstants(self):
        for constVar in global_.variablesNumbers:
            self.appendCode("SET "+constVar+"   [set const]")
            self.appendCode("STORE  @"+constVar)

    def translateProcedures(self):
        for proc in global_.instructions:
            if proc[0] == "PROCEDURE":
                self.callbackTable.append([proc[1], global_.lineCounter])
                procNameVariables = self.getVarNameInProc(proc[1])
                self.comments += " begin proc $"+proc[1]
                self.translateBlock(proc[2], proc[1], procNameVariables)
                # return to where procedure was called
                self.appendCode("JUMPI @"+proc[1]+"_JUMPBACK    [end proc $"+proc[1]+"]")

            elif proc[0] == "MAIN":
                self.callbackTable.append(["MAIN_JUMP", global_.lineCounter])
                procNameVariables = self.getVarNameInProc("MAIN")
                self.comments += " begin main"
                self.translateBlock(proc[1],"MAIN", procNameVariables)


    def translateBlock(self, block, procName, procNameVariables):

        for inst in block:
            if inst[0] == "ASSIGN":
                self.comments += " " + inst[1]+" := "+str(inst[2])
                if procName=="MAIN":
                    self.translateAssignMAIN(inst[1],inst[2], procName)
                else:
                    self.translateAssignPROC(inst[1],inst[2], procName)

            elif inst[0] == "IF":

            # Declaring pointer to jump
                jumpF = "IF_F_"+str(len(self.callbackTable))
                self.callbackTable.append([jumpF, 0])

                self.comments += " if"

                conEval = self.translateConditionMAIN if procName=="MAIN" else self.translateConditionPROC
                conEval(inst[1], procName,"IF+",jumpF)
                
                self.translateBlock(inst[2], procName, procNameVariables)
                

                # Setting value of the jump
                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == jumpF:
                        self.callbackTable[jumpNr][1] = global_.lineCounter

            elif inst[0] == "IFELSE":

                jumpF = "IFELSE_F_"+str(len(self.callbackTable))
                self.callbackTable.append([jumpF, 0])
                jumpOut = "IFELSE_O_"+str(len(self.callbackTable))
                self.callbackTable.append([jumpOut, 0])

                self.comments += " ifelse"

                conEval = self.translateConditionMAIN if procName=="MAIN" else self.translateConditionPROC
                conEval(inst[1], procName,"IFELSE+",jumpF)
                
            #### TRUE ####

                self.comments += " ifelse true"
                self.translateBlock(inst[2], procName, procNameVariables)
                self.appendCode("JUMP @"+jumpOut)

            #### FALSE ####

                # Setting value of the jump false
                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == jumpF:
                        self.callbackTable[jumpNr][1] = global_.lineCounter

                self.comments += " ifelse false"
                self.translateBlock(inst[3], procName, procNameVariables)

                # Setting value of the jump after
                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == jumpOut:
                        self.callbackTable[jumpNr][1] = global_.lineCounter

            elif inst[0] == "WHILE":

                jumpOut = "WHILE_OUT_"+str(len(self.callbackTable))
                self.callbackTable.append([jumpOut, 0])
                jumpBack = "WHILE_BACK_"+str(len(self.callbackTable))
                self.callbackTable.append([jumpBack, global_.lineCounter+1])

                self.comments += " while"

                conEval = self.translateConditionMAIN if procName=="MAIN" else self.translateConditionPROC
                conEval(inst[1], procName,"WHILE+",jumpOut)

                self.translateBlock(inst[2], procName, procNameVariables)

                self.appendCode("JUMP @"+jumpBack)

                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == jumpOut:
                        self.callbackTable[jumpNr][1] = global_.lineCounter

            elif inst[0] == "REPEAT":
                self.comments += " repeat"

                jumpBack = "REPEAT_BACK_"+str(len(self.callbackTable))
                self.callbackTable.append([jumpBack, global_.lineCounter])
                jumpOut = "REPEAT_OUT_"+str(len(self.callbackTable))
                self.callbackTable.append([jumpOut, 0])

                self.translateBlock(inst[2], procName, procNameVariables)

                conEval = self.translateConditionMAIN if procName=="MAIN" else self.translateConditionPROC
                conEval(inst[1], procName,"REPEAT+",jumpBack)


                self.appendCode("JUMP @"+jumpOut)

                for jumpNr, jumpVal in enumerate(self.callbackTable):
                    if jumpVal[0] == jumpOut:
                        self.callbackTable[jumpNr][1] = global_.lineCounter
            
            elif inst[0] == "PROC": # DONE (hope so)
                self.comments += " call proc $"+inst[1]
                for i in range(len(inst[2])):
                    self.appendCode("SET @"+procName+"_"+inst[2][i])
                    self.appendCode("STORE  @"+procNameVariables[i])
                self.appendCode("SET "+str(global_.lineCounter+2)) #TODO should it be 2 or 3
                self.appendCode("STORE  @"+inst[1]+"_JUMPBACK")
                self.appendCode("JUMP @"+inst[1])

                # self.translateBlock(inst[2], procName, procNameVariables)
                # copy values back

            elif inst[0] == "READ": 

                self.comments += " read"

                if procName=="MAIN":
                    self.appendCode("GET @"+procName+"_"+inst[1])
                else:
                    self.appendCode("GET @"+procName+"_"+inst[1])#TODO if not in main

            elif inst[0] == "WRITE":

                self.comments += " write"

                if inst[1].isnumeric():
                    valToWrite = inst[1]
                else:
                    valToWrite = procName+"_"+inst[1]


                if procName=="MAIN":
                    self.appendCode("PUT @"+valToWrite)
                else:
                    self.appendCode("LOADI @"+valToWrite)
                    self.appendCode("PUT 0")

            else:
                print("ERROR "+inst)


    def translateAssignMAIN(self,identifier,exp, procName):

        result = procName+"_"+identifier

        if exp[0].isnumeric():
            self.appendCode("SET "+exp)
            self.appendCode("STORE  @"+result)

        elif isinstance(exp, str):
            self.appendCode("LOAD   @"+procName+"_"+exp)
            self.appendCode("STORE  @"+result)

        elif isinstance(exp, list):
            exp1 = exp[1] if exp[1].isnumeric() else procName+"_"+exp[1]
            exp2 = exp[2] if exp[2].isnumeric() else procName+"_"+exp[2]

            if exp[0] == "add": 
                self.appendCode("LOAD   @"+exp1)
                self.appendCode("ADD    @"+exp2)
                self.appendCode("STORE  @"+result)

            elif exp[0] == "sub":
                self.appendCode("LOAD   @"+exp1)
                self.appendCode("SUB    @"+exp2)
                self.appendCode("STORE  @"+result)

            elif exp[0] == "mul": # multi p q
                
                self.appendCode("SET    0")                                # acc = 0
                self.appendCode("STORE  @TMP2")                          # m = acc
                self.appendCode("LOAD   @"+exp1)                          # acc = p
                                                                        # n = acc
                                                                        # should it be a line?
                self.appendCode("JZERO  "+str(global_.lineCounter+9))    # if acc = 0 break
                self.appendCode("SUB    @1")                               # acc -1
                self.appendCode("STORE  @TMP1")                          # n = acc
                self.appendCode("LOAD   @TMP2")                           # acc = m
                self.appendCode("ADD    @"+exp2)                          # acc + q
                self.appendCode("STORE  @TMP2")                          # m = acc
                self.appendCode("LOAD   @TMP1")                           # acc = n
                self.appendCode("JPOS   "+str(global_.lineCounter-6))    # jump back if positive
                self.appendCode("LOAD   @TMP2")                           # acc = m
                self.appendCode("STORE  @"+result)      # id = acc

            elif exp[0] == "div":# c = a div b

                self.appendCode("SET    0")                             # c = 0
                self.appendCode("STORE  @"+result)
                self.appendCode("LOAD   @"+exp2)                        # if b = 0
                self.appendCode("JZERO  "+str(global_.lineCounter+7+5)) #
                self.appendCode("LOAD   @"+exp1)                        # if a = 0
                self.appendCode("JZERO  "+str(global_.lineCounter+7+3)) #
                self.appendCode("ADD    @1")                            # trick add 1 for evaulation a>b
                self.appendCode("SUB    @"+exp2)
                self.appendCode("JZERO  "+str(global_.lineCounter+7))   # if !(a > b)
                self.appendCode("STORE  @TMP1")
                self.appendCode("LOAD   @"+result)                      # c++
                self.appendCode("ADD    @1")
                self.appendCode("STORE  @"+result)
                self.appendCode("LOAD   @TMP1")
                self.appendCode("JUMP   "+str(global_.lineCounter-7)+"  [end div]")   # back jump

            elif exp[0] == "mod": # c mod a b   # first div then return rest

                self.appendCode("SET    0")                             # c = 0
                self.appendCode("STORE  @"+result)
                self.appendCode("LOAD   @"+exp2)                        # if b = 0
                self.appendCode("JZERO  "+str(global_.lineCounter+7+6)) #
                self.appendCode("LOAD   @"+exp1)                        # if a = 0
                self.appendCode("JZERO  "+str(global_.lineCounter+7+4)) #
                self.appendCode("ADD    @1")                            # trick add 1 for evaulation a>b
                self.appendCode("STORE  @TMP1")                         # for a % b where a < b
                self.appendCode("SUB    @"+exp2)
                self.appendCode("JZERO  "+str(global_.lineCounter+7))   # if !(a > b)
                self.appendCode("STORE  @TMP1")
                self.appendCode("LOAD   @"+result)                      # c++
                self.appendCode("ADD    @1")
                self.appendCode("STORE  @"+result)
                self.appendCode("LOAD   @TMP1")
                self.appendCode("JUMP   "+str(global_.lineCounter-7))   # back jump
                self.appendCode("LOAD   @TMP1")
                self.appendCode("SUB    @1")
                self.appendCode("STORE  @"+result)

            else:
                print("ERROR undefined exp"+str(exp))
        else:
            print("ERROR exp wrong type"+str(exp))


    def translateAssignPROC(self,identifier,exp, procName):

        if exp[0].isnumeric():
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
                
                self.appendCode("SET    0")                            # acc = 0
                self.appendCode("STOREI @TMP2")                     # m = acc
                self.appendCode("LOADI @"+exp1)                     # acc = p
                                                                    # n = acc
                                                                    # should it be a line?
                                                                    # if acc = 0 break
                self.appendCode("JZERO  "+str(global_.lineCounter+9))
                self.appendCode("SUBI @1")                           #   acc -1
                self.appendCode("STOREI @TMP1")                      #   n = acc
                self.appendCode("LOADI @TMP2")                       # 	acc = m
                self.appendCode("ADDI @"+exp2)                       # 	acc + q
                self.appendCode("STOREI @TMP2")                      # 	m = acc
                self.appendCode("LOADI @TMP1")                       # 	acc = n
                self.appendCode("JPOS   "+str(global_.lineCounter-6)) # 	jump back if
                self.appendCode("LOADI @TMP2")                       # acc = m
                self.appendCode("STOREI @"+procName+"_"+identifier)  # id = acc

            elif exp[0] == "div":# div p d

                self.appendCode("SET    0")                                # result = 0
                self.appendCode("STOREI @TMP1")
                self.appendCode("LOADI @"+exp2)                         # if d = 0 jump_out
                self.appendCode("JZERO  "+str(global_.lineCounter+13))   # jump out
                self.appendCode("LOADI @"+exp1)                         # rest = p
                self.appendCode("STOREI @TMP2")
                self.appendCode("SUBI @"+exp2)                          # acc = rest - d
                self.appendCode("JZERO  "+str(global_.lineCounter+9))    # if 0 jump_out
                self.appendCode("STOREI @TMP2")                         # rest = acc
                self.appendCode("SET    1")                                # result + 1
                self.appendCode("ADDI @TMP1")
                self.appendCode("STOREI @TMP1")
                self.appendCode("LOADI @TMP2")                          # acc = rest - d
                self.appendCode("SUBI @"+exp2)
                self.appendCode("JUMP "+str(global_.lineCounter-7))     # jump back to if
                self.appendCode("LOADI @TMP1")                          # id = result
                self.appendCode("STOREI @"+procName+"_"+identifier)

            elif exp[0] == "mod": # mod p d

                self.appendCode("SET    0")                                # result = 0
                self.appendCode("STOREI @TMP1")
                self.appendCode("LOADI @"+exp2)                         # if d = 0 jump_out
                self.appendCode("JZERO  "+str(global_.lineCounter+13))   # jump out
                self.appendCode("LOADI @"+exp1)                         # rest = p
                self.appendCode("STOREI @TMP2")
                self.appendCode("SUBI @"+exp2)                          # acc = rest - d
                self.appendCode("JZERO  "+str(global_.lineCounter+9))    # if 0 jump_out
                self.appendCode("STOREI @TMP2")                         # rest = acc
                self.appendCode("SET    1")                                # result + 1
                self.appendCode("ADDI @TMP1")
                self.appendCode("STOREI @TMP1")
                self.appendCode("LOADI @TMP2")                          # acc = rest - d
                self.appendCode("SUBI @"+exp2)
                self.appendCode("JUMP "+str(global_.lineCounter-7))     #jump back to if
                self.appendCode("LOADI @TMP2")                          # id = rest
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

        self.comments += str(cond)

        if cond[0] == "eq":
                                                                # 3 4           # 5 4
            self.appendCode("SET    1")                         # acc = 1       # acc = 1
            self.appendCode("ADD    @"+cond1)                   # acc = 4       # acc = 6
            self.appendCode("SUB    @"+cond2)                   # acc = 0       # acc = 2
            self.appendCode("JZERO  @"+jumpF)                   # NOT jump_out  # NO action
            self.appendCode("SUB    @1")                        # acc = 0       # acc = 1
            self.appendCode("JPOS   @"+jumpF)                   #               # NOT jump_out
        elif cond[0] == "ne":

            self.appendCode("SET    1")                             # acc = 1       # acc = 1
            self.appendCode("ADD    @"+cond1)                       # acc = 4       # acc = 6
            self.appendCode("SUB    @"+cond2)                       # acc = 0       # acc = 2
            self.appendCode("JZERO  "+str(global_.lineCounter+4))   # NOT jump_out  # NO action
            self.appendCode("SUB    @1")                            # acc = 0       # acc = 1
            self.appendCode("JPOS   "+str(global_.lineCounter+2))   #               # NOT jump_out
            self.appendCode("JUMP   @"+jumpF)

        elif cond[0] == "gt":   # a > b

            self.appendCode("LOAD   @"+cond1)
            self.appendCode("SUB    @"+cond2)
            self.appendCode("JPOS   "+str(global_.lineCounter+2))
            self.appendCode("JUMP   @"+jumpF)

        elif cond[0] == "ge":

            self.appendCode("SET    1")
            self.appendCode("ADD    @"+cond1)
            self.appendCode("SUB    @"+cond2)
            self.appendCode("JPOS   "+str(global_.lineCounter+2))
            self.appendCode("JUMP   @"+jumpF)
            
        else:
            self.appendCode("ERROR "+cond)

    def translateConditionPROC(self,cond, procName,codePointer,jumpF):
        
        # Fix that some values are constants
        cond1 = cond[1] if cond[1].isnumeric() else procName+"_"+cond[1]
        cond2 = cond[2] if cond[2].isnumeric() else procName+"_"+cond[2]     

        self.callbackTable.append([codePointer, global_.lineCounter])
        
        if cond[0] == "eq":
                                                             # 2 3       # 3 2
            self.appendCode("SET    1")                         # acc = 1   # acc = 1
            self.appendCode("ADDI @"+cond1)                  # acc = 2   # acc = 4
            self.appendCode("SUBI @"+cond2)                  # acc = 0   # acc = 2
            self.appendCode("JPOS   @"+jumpF)                  # JUMP OUT  # nothing
            self.appendCode("SUBI @1")                       #           # acc = 1
            self.appendCode("JPOS   @"+jumpF)                  #           # JUMP OUT
            
        elif cond[0] == "ne":
                                                             # 3 4           # 5 4
            self.appendCode("SET    1")                         # acc = 1       # acc = 1
            self.appendCode("ADDI @"+cond1)                  # acc = 4       # acc = 6
            self.appendCode("SUBI @"+cond2)                  # acc = 0       # acc = 2
            self.appendCode("JZERO  @"+jumpF)                 # NOT jump_out  # NO action
            self.appendCode("SUBI @1")                       # acc = 0       # acc = 1
            self.appendCode("JPOS   @"+jumpF)                  #               # NOT jump_out
            
        elif cond[0] == "gt":   # 

            self.appendCode("LOADI @"+cond1)
            self.appendCode("SUBI @"+cond2)
            self.appendCode("JPOS   @"+jumpF)

        elif cond[0] == "ge":

            self.appendCode("SET    1")
            self.appendCode("ADDI @"+cond1)
            self.appendCode("SUBI @"+cond2)
            self.appendCode("JPOS   @"+jumpF)
            
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