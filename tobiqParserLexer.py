from sly import Parser, Lexer
import tobiqContext_

class TobiqLexer(Lexer):
    tokens = {IDENTIFIER, NUM,
            PROCEDURE, IS, VAR, END, BEGIN, PROGRAM,
            IF, THEN, ELSE, ENDIF,
            WHILE, DO, ENDWHILE,
            REPEAT, UNTIL,
            READ, WRITE,
            GETS, NEQ, GEQ, LEQ, EQ, GT, LT}
    literals = {'+', '-', '*', '/', '%', ',', ';', '(', ')'}
    ignore = ' \s'
    ignore_tab = ' \t'
    ignore_comment = r'[\[][^\]]*[\]]'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1

    PROCEDURE   = r"PROCEDURE"
    IS          = r"IS"
    VAR         = r"VAR"
    ENDIF       = r"ENDIF"
    ENDWHILE    = r"ENDWHILE"
    END         = r"END"
    BEGIN       = r"BEGIN"
    PROGRAM     = r"PROGRAM"
    IF          = r"IF"
    THEN        = r"THEN"
    ELSE        = r"ELSE"
    WHILE       = r"WHILE"
    DO          = r"DO"
    REPEAT      = r"REPEAT"
    UNTIL       = r"UNTIL"
    READ        = r"READ"
    WRITE       = r"WRITE"

    GETS    = r":="
    NEQ     = r"!="
    GEQ     = r">="
    LEQ     = r"<="
    EQ      = r"="
    GT      = r">"
    LT      = r"<"

    IDENTIFIER = r'[_a-zA-Z]+'
    NUM        = r'\d+'

class TobiqParser(Parser):
    tokens = TobiqLexer.tokens
    code = None

    @_('procedures main')
    def program_all(self, p):
        pass
        # print("program_all")

    @_('procedures PROCEDURE proc_head IS VAR declarations BEGIN commands END')
    def procedures(self, p):
        tobiqContext_.proceduresNames.append(p[2][0])
        tobiqContext_.variablesNames.append("1ump")
        for i in range(len(tobiqContext_.variablesNames)):
            if not ' ' in tobiqContext_.variablesNames[i]: # if varName one word concat name of procedure in front
                tobiqContext_.variablesNames[i] = tobiqContext_.proceduresNames[-1] + " " + tobiqContext_.variablesNames[i]
        print("PROC_DEF_VAR", p[2][0], p[2][1], p[5], p[7])

    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        tobiqContext_.proceduresNames.append(p[2][0])
        tobiqContext_.variablesNames.append("1ump")
        for i in range(len(tobiqContext_.variablesNames)):
            if not ' ' in tobiqContext_.variablesNames[i]: # if varName one word concat name of procedure in front
                tobiqContext_.variablesNames[i] = tobiqContext_.proceduresNames[-1] + " " + tobiqContext_.variablesNames[i]
        print("PROC_DEF", p[2][0], p[2][1], p[5])

    @_('empty')
    def procedures(self, p):
        pass
        # print("procedures_empty")

    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        tobiqContext_.proceduresNames.append("main")
        tobiqContext_.variablesNames.append("1ump")
        for i in range(len(tobiqContext_.variablesNames)):
            if not ' ' in tobiqContext_.variablesNames[i]: # if varName one word concat name of procedure in front
                tobiqContext_.variablesNames[i] = tobiqContext_.proceduresNames[-1] + " " + tobiqContext_.variablesNames[i]

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        tobiqContext_.proceduresNames.append("main")
        tobiqContext_.variablesNames.append("1ump")
        for i in range(len(tobiqContext_.variablesNames)):
            if not ' ' in tobiqContext_.variablesNames[i]: # if varName one word concat name of procedure in front
                tobiqContext_.variablesNames[i] = tobiqContext_.proceduresNames[-1] + " " + tobiqContext_.variablesNames[i]
        

    @_('commands command')
    def commands(self, p):
        return p[0], p[1]

    @_('command')
    def commands(self, p):
        return p[0]
        # print('command_GETS')

    @_('IDENTIFIER GETS expression ";"')
    def command(self, p):
        print("GETS", p[0], p[2])
        return "GETS", p[0], p[2]

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        print("IFELSE", p[1], p[3], p[5])
        return "IFELSE", p[1], p[3], p[5]

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        print("IF", p[1], p[3])
        return "IF", p[1], p[3]

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        print("WHILE", p[1], p[3])
        return "WHILE", p[1], p[3]

    @_('REPEAT commands UNTIL condition ";"')
    def command(self, p):
        print("REPEAT", p[1], p[3])
        return "REPEAT", p[1], p[3]


    @_('proc_head ";"')
    def command(self, p):
        if not p[0][0] in tobiqContext_.proceduresNames:
            print(tobiqContext_.proceduresNames)
            print(">>> Undeclared procedure =",p[0][0])
            return SyntaxError
        else:
            print("PROC", p[0][0], p[0][1])
            return "PROC", p[0][0], p[0][1]

    @_('READ IDENTIFIER ";"')
    def command(self, p):
        print("READ", p[1])
        return "READ", p[1]

    @_('WRITE value ";"')
    def command(self, p):
        print("WRITE", p[1])
        return "WRITE", p[1]

    @_('IDENTIFIER "(" declarations ")"')
    def proc_head(self, p):
        # print("proc_head = ", p[0])
        return p[0], p[2]

    @_('declarations "," IDENTIFIER')
    def declarations(self, p):
        # print("declarations_,_IDENTIFIER = ",p[2])
        tobiqContext_.variablesNames.append(p[2])
        return p[0], p[2]

    @_('IDENTIFIER')
    def declarations(self, p):
        # print("declarations_IDENTIFIER = ",p[0])
        tobiqContext_.variablesNames.append(p[0])
        return p[0]

    @_('value')
    def expression(self, p):
        print("EXP_VAL", p[0])
        return "EXP_VAL", p[0]

    @_('value "+" value')
    def expression(self, p):
        print("EXP_ADD", p[0], p[2])
        return "EXP_ADD", p[0], p[2]

    @_('value "-" value')
    def expression(self, p):
        print("EXP_SUB", p[0], p[2])
        return "EXP_SUB", p[0], p[2]

    @_('value "*" value')
    def expression(self, p):
        print("EXP_MULTI", p[0], p[2])
        return "EXP_MULTI", p[0], p[2]

    @_('value "/" value')
    def expression(self, p):
        print("EXP_DIV", p[0], p[2])
        return "EXP_DIV", p[0], p[2]

    @_('value "%" value')
    def expression(self, p):
        print("EXP_MOD", p[0], p[2])
        return "EXP_MOD", p[0], p[2]

    @_('value EQ value')
    def condition(self, p):
        print("CON_EQ", p[0], p[2])
        return "CON_EQ", p[0], p[2]

    @_('value NEQ value')
    def condition(self, p):
        print("CON_NEQ", p[0], p[2])
        return "CON_NEQ", p[0], p[2]

    @_('value GT value')
    def condition(self, p):
        print("CON_GT", p[0], p[2])
        return "CON_GT", p[0], p[2]

    @_('value LT value')
    def condition(self, p):
        print("CON_GT", p[2], p[0])
        return "CON_GT", p[2], p[0]

    @_('value LEQ value')
    def condition(self, p):
        print("CON_GEQ", p[2], p[0])
        return "CON_GEQ", p[2], p[0]

    @_('value GEQ value')
    def condition(self, p):
        print("CON_GEQ", p[0], p[2])
        return "CON_GEQ", p[0], p[2]


    @_('NUM')
    def value(self, p):
        # print("value_num = ", p[0])
        return p[0]


    @_('IDENTIFIER')
    def value(self, p):
        if not p[0] in tobiqContext_.variablesNames:
            print(">>> Undeclared variable = ", p[0])
            return SyntaxError
        else:
            # print("value_IDENTIFIER = ", p[0])
            return p[0]

    @_('')
    def empty(self, p):
        pass

