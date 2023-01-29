lineNumber          = 0         # for lexer/parser
# if lexer and parser merged could be not so global
lineCounter         = 0         # for translator and jumps
variablesNames      = []        # usage Compilator, Parser, Translator
variablesNumbers    = ["1"]     # for adding to #Parser, Translator
variableInit        = []        # only in Parser, always with variablesNames