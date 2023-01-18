from sly import Lexer
import tobiqContext_

class MyLexer(Lexer):
    tokens = {IDENTIFIER, NUM,
            PROCEDURE, IS, VAR, END, BEGIN, PROGRAM,
            IF, THEN, ELSE, ENDIF,
            WHILE, DO, ENDWHILE,
            REPEAT, UNTIL,
            READ, WRITE,
            GETS, NEQ, GEQ, LEQ, EQ, GT, LT}
    literals = {'+', '-', '*', '/', '%', ',', ';', '(', ')', ' , '}
    ignore = ' \t'

    ignore_comment = r'[[][^]]*[]]'


    @_(r'\n+')
    def ignore_newline(self, t):
        tobiqContext_.line_number+=1


    def error(self, t):
        raise Exception(f"Illegal character '{t.value[0]}'")

    PROCEDURE   = r"PROCEDURE"
    IS          = r"IS"
    VAR         = r"VAR"
    BEGIN       = r"BEGIN"
    PROGRAM     = r"PROGRAM"
    IF          = r"IF"
    THEN        = r"THEN"
    ELSE        = r"ELSE"
    ENDWHILE    = r"ENDWHILE"
    ENDIF       = r"ENDIF"
    END         = r"END"
    WHILE       = r"WHILE"
    DO          = r"DO"
    REPEAT      = r"REPEAT"
    UNTIL       = r"UNTIL"
    READ        = r"READ"
    WRITE       = r"WRITE"

    GETS = r":="
    NEQ = r"!="
    GEQ = r">="
    LEQ = r"<="
    EQ = r"="
    GT = r">"
    LT = r"<"
    IDENTIFIER = r"[_a-z]+"
    NUM = r'\d+'
