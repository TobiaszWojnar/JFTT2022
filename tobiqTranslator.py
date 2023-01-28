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

        # print("######### callbackTable ##########")
        # print(self.callbackTable)

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
                    self.translateAssign(inst[1],inst[2], procName)

            elif inst[0] == "IF":

            # Declaring pointer to jump
                jumpF = "IF_F_"+str(len(self.callbackTable))
                self.callbackTable.append([jumpF, 0])

                self.comments += " if"

                self.translateCondition(inst[1], procName,"IF+",jumpF)
                
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

                self.translateCondition(inst[1], procName,"IFELSE+",jumpF)
                
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

                self.translateCondition(inst[1], procName,"WHILE+",jumpOut)

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

                self.translateCondition(inst[1], procName,"REPEAT+",jumpBack)


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


    def translateAssign(self,identifier,exp, procName):


        if procName+"_"+identifier in global_.variablesNames:
            resultEND = "  @"+procName+"_"+identifier
        else:
            resultEND = "I @"+procName+"^"+identifier

        if exp[0].isnumeric():                          #### TODO should be able to colapse into one 
            self.appendCode("SET "+exp)
            self.appendCode("STORE"+resultEND)

        elif isinstance(exp, str):
            if procName+"_"+exp in global_.variablesNames:
                self.appendCode("LOAD   @"+procName+"_"+exp)
            else:
                self.appendCode("LOADI  @"+procName+"^"+exp)                
            self.appendCode("STORE"+resultEND)

        elif isinstance(exp, list):
            exp1END = self.getInstrSufixForVar(exp[1],procName)
            exp2END = self.getInstrSufixForVar(exp[2],procName)

            if exp[0] == "add": 
                self.appendCode("LOAD"+exp1END)
                self.appendCode("ADD"+exp2END)
                self.appendCode("STORE"+resultEND)

            elif exp[0] == "sub":
                self.appendCode("LOAD"+exp1END)
                self.appendCode("SUB"+exp2END)
                self.appendCode("STORE"+resultEND)

            elif exp[0] == "mul": # multi p q
                
                self.appendCode("SET    0")                                # acc = 0
                self.appendCode("STORE  @TMP2")                          # m = acc
                self.appendCode("LOAD"+exp1END)                          # acc = p
                                                                        # n = acc
                                                                        # should it be a line?
                self.appendCode("JZERO  "+str(global_.lineCounter+9))    # if acc = 0 break
                self.appendCode("SUB    @1")                               # acc -1
                self.appendCode("STORE  @TMP1")                          # n = acc
                self.appendCode("LOAD   @TMP2")                           # acc = m
                self.appendCode("ADD"+exp2END)                          # acc + q
                self.appendCode("STORE  @TMP2")                          # m = acc
                self.appendCode("LOAD   @TMP1")                           # acc = n
                self.appendCode("JPOS   "+str(global_.lineCounter-6))    # jump back if positive
                self.appendCode("LOAD   @TMP2")                           # acc = m
                self.appendCode("STORE"+resultEND)                                               # id = acc

            elif exp[0] == "div":# c = a div b

                self.appendCode("SET    0")                             # c = 0
                self.appendCode("STORE  @TMP2")
                self.appendCode("LOAD"+exp2END)                        # if b = 0
                self.appendCode("JZERO  "+str(global_.lineCounter+7+5)) #
                self.appendCode("LOAD"+exp1END)                        # if a = 0
                self.appendCode("JZERO  "+str(global_.lineCounter+7+3)) #
                self.appendCode("ADD    @1")                            # trick add 1 for evaulation a>b
                self.appendCode("SUB"+exp2END)
                self.appendCode("JZERO  "+str(global_.lineCounter+7))   # if !(a > b)
                self.appendCode("STORE  @TMP1")
                self.appendCode("LOAD   @TMP2")                      # c++
                self.appendCode("ADD    @1")
                self.appendCode("STORE  @TMP2")
                self.appendCode("LOAD   @TMP1")
                self.appendCode("JUMP   "+str(global_.lineCounter-7)+"  [end div]")   # back jump
                self.appendCode("LOAD   @TMP2")
                self.appendCode("STORE"+resultEND)

            elif exp[0] == "mod": # c mod a b   # first div then return rest

                self.appendCode("SET    0")                             # c = 0
                self.appendCode("STORE  @TMP2")
                self.appendCode("LOAD"+exp2END)                        # if b = 0
                self.appendCode("JZERO  "+str(global_.lineCounter+7+6)) #
                self.appendCode("LOAD"+exp1END)                        # if a = 0
                self.appendCode("JZERO  "+str(global_.lineCounter+7+4)) #
                self.appendCode("ADD    @1")                            # trick add 1 for evaulation a>b
                self.appendCode("STORE  @TMP1")                         # in case a % b and  b>a
                self.appendCode("SUB"+exp2END)
                self.appendCode("JZERO  "+str(global_.lineCounter+7))   # if !(a > b)
                self.appendCode("STORE  @TMP1")
                self.appendCode("LOAD   @TMP2")                             # c++
                self.appendCode("ADD    @1")
                self.appendCode("STORE  @TMP2")
                self.appendCode("LOAD   @TMP1")
                self.appendCode("JUMP   "+str(global_.lineCounter-7)+"  [end div]")   # back jump
                self.appendCode("LOAD   @TMP1")
                self.appendCode("SUB    @1")
                self.appendCode("STORE"+resultEND)

            else:
                print("ERROR undefined exp"+str(exp))
        else:
            print("ERROR exp wrong type"+str(exp))

    def translateCondition(self,cond, procName,codePointer,jumpF):

        # Fix that some values are constants
        cond1END = self.getInstrSufixForVar(cond[1],procName)
        cond2END = self.getInstrSufixForVar(cond[2],procName)

        self.callbackTable.append([codePointer, global_.lineCounter])

        self.comments += str(cond)

        if cond[0] == "eq":
                                                                # 3 4           # 5 4
            self.appendCode("SET    1")                         # acc = 1       # acc = 1
            self.appendCode("ADD"+cond1END)                   # acc = 4       # acc = 6
            self.appendCode("SUB"+cond2END)                     # acc = 0       # acc = 2
            self.appendCode("JZERO  @"+jumpF)                   # NOT jump_out  # NO action
            self.appendCode("SUB    @1")                        # acc = 0       # acc = 1
            self.appendCode("JPOS   @"+jumpF)                   #               # NOT jump_out
        elif cond[0] == "ne":

            self.appendCode("SET    1")                             # acc = 1       # acc = 1
            self.appendCode("ADD"+cond1END)                         # acc = 4       # acc = 6
            self.appendCode("SUB"+cond2END)                         # acc = 0       # acc = 2
            self.appendCode("JZERO  "+str(global_.lineCounter+4))   # NOT jump_out  # NO action
            self.appendCode("SUB    @1")                            # acc = 0       # acc = 1
            self.appendCode("JPOS   "+str(global_.lineCounter+2))   #               # NOT jump_out
            self.appendCode("JUMP   @"+jumpF)

        elif cond[0] == "gt":   # a > b

            self.appendCode("LOAD"+cond1END)  
            self.appendCode("SUB"+cond2END)  
            self.appendCode("JPOS   "+str(global_.lineCounter+2))
            self.appendCode("JUMP   @"+jumpF)

        elif cond[0] == "ge":

            self.appendCode("SET    1")
            self.appendCode("ADD"+cond1END)  
            self.appendCode("SUB"+cond2END)  
            self.appendCode("JPOS   "+str(global_.lineCounter+2))
            self.appendCode("JUMP   @"+jumpF)
            
        else:
            self.appendCode("ERROR "+cond)


    def getVarNameInProc(self, procName):
        result=[]
        for var in global_.variablesNames:
            if var.startswith(procName):
                result.append(var)
        return result

    def getInstrSufixForVar(self, varName, procName):
        if varName.isnumeric():
            expEND = "   @"+varName
        elif procName+"_"+varName in global_.variablesNames:
            expEND = "   @"+procName+"_"+varName
        else:
            expEND = "I  @"+procName+"^"+varName

        return expEND

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