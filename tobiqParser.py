from sly import Parser
from tobiqLexer import MyLexer
import tobiqContext_

class MyParser(Parser):    
    tokens = MyLexer.tokens
    declaringNewVariablesLock = True
    tmpVariables = []

    @_('procedures main')
    def program_all(self, p):

        tobiqContext_.variablesNames = ["acc","1","tmp1","tmp2","multi","tmp3"]+tobiqContext_.variablesNames

        if p[0] != None:
            tobiqContext_.instructions = p[0],p[1]
            return p[0],p[1]
        else:
            tobiqContext_.instructions = p[1]
            return p[1]

    @_('procedures PROCEDURE proc_head IS VAR declarations BEGIN commands END')
    def procedures(self, p):
        duplicates = duplicatesFinder(p[2][1]+p[5])
        if len(duplicates) > 0:
            print("ERROR: Secondary declaration of variables = ", duplicates)

        tobiqContext_.proceduresNames.append([p[2][0],len(p[2][1])])
        tobiqContext_.variablesNames.append("1ump")
        for i in range(len(tobiqContext_.variablesNames)):
            if not ' ' in tobiqContext_.variablesNames[i]: # if varName one word concat name of procedure in front
                tobiqContext_.variablesNames[i] = tobiqContext_.proceduresNames[-1][0] + " " + tobiqContext_.variablesNames[i]
        if p[0] != None:
            return p[0]+["PROCEDURE" , p[2] , p[7]]# p[5],
        else:
            return ["PROCEDURE" , p[2] , p[7]]# p[5],

    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        duplicates = duplicatesFinder(p[2][1])
        if len(duplicates) > 0:
            print("ERROR: Secondary declaration of variables = ", duplicates)

        tobiqContext_.proceduresNames.append([p[2][0],len(p[2][1])])
        tobiqContext_.variablesNames.append("1ump")
        for i in range(len(tobiqContext_.variablesNames)):
            if not ' ' in tobiqContext_.variablesNames[i]: # if varName one word concat name of procedure in front
                tobiqContext_.variablesNames[i] = tobiqContext_.proceduresNames[-1][0] + " " + tobiqContext_.variablesNames[i]
        if p[0] != None:
            return p[0]+["PROCEDURE" , p[2] , p[5]]
        else:
            return ["PROCEDURE" , p[2] , p[5]]

    @_('empty')
    def procedures(self, p):
        return

    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        duplicates = duplicatesFinder(p[3])
        if len(duplicates) > 0:
            print("ERROR: Secondary declaration of variables = ", duplicates)

        tobiqContext_.proceduresNames.append(["main",])
        tobiqContext_.variablesNames.append("1ump")
        for i in range(len(tobiqContext_.variablesNames)):
            if not ' ' in tobiqContext_.variablesNames[i]: # if varName one word concat name of procedure in front
                tobiqContext_.variablesNames[i] = tobiqContext_.proceduresNames[-1][0] + " " + tobiqContext_.variablesNames[i]
        return ["PROGRAM" , p[3] , p[5]]

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        tobiqContext_.proceduresNames.append(["main",])
        tobiqContext_.variablesNames.append("1ump")
        for i in range(len(tobiqContext_.variablesNames)):
            if not ' ' in tobiqContext_.variablesNames[i]: # if varName one word concat name of procedure in front
                tobiqContext_.variablesNames[i] = tobiqContext_.proceduresNames[-1][0] + " " + tobiqContext_.variablesNames[i]
        return ["PROGRAM" , p[3]]

    @_('commands command')
    def commands(self, p):
        return p[0] + [p[1]]

    @_('command')
    def commands(self, p):
        return [p[0]]

    @_('IDENTIFIER GETS expression ";"')
    def command(self, p):
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
        #TODO DO we want commands, cond || cond, commands

    @_('proc_head ";"')
    def command(self, p):
        fuckup = True
        for i in tobiqContext_.proceduresNames:
            if p[0][0] == i[0]:
                fuckup = False
        if fuckup:
            print("ERROR. Undeclared procedure = ", p[0][0], " in line ", tobiqContext_.line_number)
            return SyntaxError

        fuckup = True
        for i in tobiqContext_.proceduresNames:
            if p[0][0] == i[0] and len(p[0][1]) == i[1]:
                fuckup = False
        if fuckup:
            print("ERROR. Wrong number of arguments ", p[0][0], " ", p[0][1], " in line ", tobiqContext_.line_number)
            return SyntaxError
        else:
            return ["PROC", p[0][0], p[0][1]]

    @_('READ IDENTIFIER ";"')
    def command(self, p):
        return ["READ", p[1]]

    @_('WRITE value ";"')
    def command(self, p):
        return ["WRITE", p[1]]

    @_('IDENTIFIER "(" declarations ")"')
    def proc_head(self, p):
        return p[0], p[2]

    @_('declarations "," IDENTIFIER')
    def declarations(self, p):
        if not  p[2] in tobiqContext_.variablesNames:
            tobiqContext_.variablesNames.append(p[2]) #TODO check if already is
        return p[0] + [p[2]]

    @_('IDENTIFIER')
    def declarations(self, p):
        if not  p[0] in tobiqContext_.variablesNames:
            tobiqContext_.variablesNames.append(p[0]) #TODO check if already is
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
        if not p[0] in tobiqContext_.variablesNames:
            print("ERROR. Undeclared variable = ", p[0], " in line ", tobiqContext_.line_number)
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
