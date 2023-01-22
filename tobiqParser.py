from sly import Parser
from tobiqLexer import TobiqLexer
import tobiqContext_ as global_
# from tobiqContext_ import variablesNames
# from tobiqContext_ import instructions
# from tobiqContext_ import global_.proceduresNames
# from tobiqContext_ import global_.variableInit
# from tobiqContext_ import global_.lineNumber


class TobiqParser(Parser):    
    tokens = TobiqLexer.tokens
    declaringNewVariablesLock = True
    code = None
    isInitTrue = True
    #TODO for now works with one function
    # change to do we add False on exit identifier procedures
    # will work for only one?
    # on exit z procedury make true
    # on empty make false

    @_('procedures main')
    def program_all(self, p):

        global_.variablesNames = ["acc","1","tmp1","tmp2","multi","tmp3"]+global_.variablesNames

        if p[0] != None:
            global_.instructions = p[0]+p[1]
            return p[0]+p[1]
        else:
            global_.instructions = p[1]
            return p[1]

    @_('procedures PROCEDURE proc_head IS VAR declarations BEGIN commands END')
    def procedures(self, p):
        duplicates = duplicatesFinder(p[2][1]+p[5])
        if len(duplicates) > 0:
            print("ERROR: Secondary declaration of variables = ", duplicates)

        global_.proceduresNames.append([p[2][0],len(p[2][1])])
        global_.variablesNames.append("1ump")
        global_.variableInit.append(True)

        for i in range(len(global_.variablesNames)):
            if not ' ' in global_.variablesNames[i]: # if varName one word concat name of procedure in front
                global_.variablesNames[i] = global_.proceduresNames[-1][0] + " " + global_.variablesNames[i]
        if p[0] != None:
            return p[0]+[[["PROCEDURE" , p[2][0] , p[7]]]]# p[5],
        else:
            return ["PROCEDURE" , p[2][0] , p[7]]# p[5],

    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        duplicates = duplicatesFinder(p[2][1])
        if len(duplicates) > 0:
            print("ERROR: Secondary declaration of variables = ", duplicates)

        global_.proceduresNames.append([p[2][0],len(p[2][1])])
        global_.variablesNames.append("1ump")
        global_.variableInit.append(True)

        # self.isInitTrue = True

        for i in range(len(global_.variablesNames)):
            if not ' ' in global_.variablesNames[i]: # if varName one word concat name of procedure in front
                global_.variablesNames[i] = global_.proceduresNames[-1][0] + " " + global_.variablesNames[i]
        procedureBody = [["PROCEDURE", [p[2][0]], p[5]]]
        if p[0] != None:
            return p[0]+procedureBody
        else:
            return procedureBody

    @_('empty')
    def procedures(self, p):
        # self.isInitTrue = False
        return

    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        duplicates = duplicatesFinder(p[3])
        if len(duplicates) > 0:
            print("ERROR: Secondary declaration of variables = ", duplicates)

        global_.proceduresNames.append(["ma1n",])
        global_.variablesNames.append("1ump")
        global_.variableInit.append(True)
        for i in range(len(global_.variablesNames)):
            if not ' ' in global_.variablesNames[i]: # if varName one word concat name of procedure in front
                global_.variablesNames[i] = global_.proceduresNames[-1][0] + " " + global_.variablesNames[i]
        return [["PROGRAM", p[5]]]

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        global_.proceduresNames.append(["ma1n",])
        global_.variablesNames.append("1ump")
        global_.variableInit.append(True)
        for i in range(len(global_.variablesNames)):
            if not ' ' in global_.variablesNames[i]: # if varName one word concat name of procedure in front
                global_.variablesNames[i] = global_.proceduresNames[-1][0] + " " + global_.variablesNames[i]
        return ["PROGRAM" , p[3]]

    @_('commands command')
    def commands(self, p):
        return p[0] + [p[1]]

    @_('command')
    def commands(self, p):
        return [p[0]]

    @_('IDENTIFIER GETS expression ";"')
    def command(self, p):

        # Checks if identifier is initialized or is a constant before usage
        if p[2][0] in ["add","sub","mul","div","mod"]: 
            if initChecker(p[2][1]) and initChecker(p[2][2]):
                global_.variableInit[global_.variablesNames.index(p[0])] = True
        else:
            if initChecker(p[2]):
                global_.variableInit[global_.variablesNames.index(p[0])] = True
        return ["ASSIGN" , p[0] , p[2]]

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return ["IFELSE", p[1], p[3], p[5]]

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return ["IF", p[1], p[3]]

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return ["WHILE", p[1], p[3]]

    @_('REPEAT commands UNTIL condition ";"')
    def command(self, p):
        return ["REPEAT", p[1], p[3]]

    @_('proc_head ";"')
    def command(self, p):
        fuckup = True
        for i in global_.proceduresNames:
            if p[0][0] == i[0]:
                fuckup = False
        if fuckup:
            print("ERROR. Undeclared procedure = ", p[0][0], " in line ", global_.lineNumber)
            return SyntaxError

        fuckup = True
        for i in global_.proceduresNames:
            if p[0][0] == i[0] and len(p[0][1]) == i[1]:
                fuckup = False
        if fuckup:
            print("ERROR. Wrong number of arguments ", p[0][0], " ", p[0][1], " in line ", global_.lineNumber)
            return SyntaxError
        else:
            return ["PROC", p[0][0], p[0][1]]

    @_('READ IDENTIFIER ";"')
    def command(self, p):
        global_.variableInit[global_.variablesNames.index(p[1])] = True
        return ["READ", p[1]]

    @_('WRITE value ";"')
    def command(self, p):
        initChecker(p[1])
        return ["WRITE", p[1]]

    @_('IDENTIFIER "(" declarations ")"')
    def proc_head(self, p):
        self.isInitTrue = False
        for id in p[2]:
            idIndex = global_.variablesNames.index(id)
            if not global_.variableInit[idIndex]:
                global_.variableInit[idIndex] = True # TODO may not be ok maybe warning?
        return p[0], p[2]

    @_('declarations "," IDENTIFIER')
    def declarations(self, p):
        if not  p[2] in global_.variablesNames:
            global_.variablesNames.append(p[2])
            global_.variableInit.append(self.isInitTrue)
        return p[0] + [p[2]]

    @_('IDENTIFIER')
    def declarations(self, p):
        if not  p[0] in global_.variablesNames:
            global_.variablesNames.append(p[0])
            global_.variableInit.append(self.isInitTrue)
        return [p[0]]

    @_('value')
    def expression(self, p):
        return p[0]

    @_('value "+" value')
    def expression(self, p):
        return "add", p[0], p[2]

    @_('value "-" value')
    def expression(self, p):
        return "sub", p[0], p[2]

    @_('value "*" value')
    def expression(self, p):
        return "mul", p[0], p[2]

    @_('value "/" value')
    def expression(self, p):
        return "div", p[0], p[2]

    @_('value "%" value')
    def expression(self, p):
        return "mod", p[0], p[2]

    @_('value EQ value')
    def condition(self, p):
        return "eq", p[0], p[2]

    @_('value NEQ value')
    def condition(self, p):
        return "ne", p[0], p[2]

    @_('value LT value')
    def condition(self, p):
        return "gt", p[2], p[0]

    @_('value GT value')
    def condition(self, p):
        return "gt", p[0], p[2]

    @_('value LEQ value')
    def condition(self, p):
        return "ge", p[2], p[0]

    @_('value GEQ value')
    def condition(self, p):
        return ["ge", p[0], p[2]]

    @_('NUM')
    def value(self, p):
        return p[0]

    @_('IDENTIFIER')
    def value(self, p):
        if not p[0] in global_.variablesNames:
            print("ERROR. Undeclared variable = ", p[0], " in line ", global_.lineNumber)
            return SyntaxError
        else:
            return p[0]

    @_('')
    def empty(self, p):
        pass


def duplicatesFinder(myList):
    newList = [] # empty list to hold unique elements from the list
    dupList = [] # empty list to hold the duplicate elements from the list
    for i in myList:
        if i not in newList:
            newList.append(i)
        else:
            dupList.append(i)
    return dupList

def initChecker(identifier):
    if identifier.isnumeric() or global_.variableInit[global_.variablesNames.index(identifier)]:
        return True
    else:
        print("ERROR. Uninitialized Usage = ", identifier, " in line ", global_.lineNumber)
        return NameError