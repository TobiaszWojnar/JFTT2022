from sly import Parser
from tobiqLexer import MyLexer
import tobiqContext_

class MyParser(Parser):    
    tokens = MyLexer.tokens

    @_('procedures main')
    def program_all(self, p):
        if p[0] != None:
            tobiqContext_.instructions = p[0],p[1]
            return p[0],p[1]
        else:
            tobiqContext_.instructions = p[1]
            return p[1]

    @_('procedures PROCEDURE proc_head IS VAR declarations BEGIN commands END')
    def procedures(self, p):
        if p[0] != None:
            return p[0]+["PROCEDURE" , p[2] , p[7]]# p[5],
        else:
            return ["PROCEDURE" , p[2] , p[7]]# p[5],

    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        if p[0] != None:
            return p[0]+["PROCEDURE" , p[2] , p[5]]
        else:
            return ["PROCEDURE" , p[2] , p[5]]

    @_('empty')
    def procedures(self, p):
        return

    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        return ["PROGRAM" , p[3] , p[5]]

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
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
        return p[0] + [p[2]]

    @_('IDENTIFIER')
    def declarations(self, p):
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
        return p[0]

    @_('')
    def empty(self, p):
        pass
