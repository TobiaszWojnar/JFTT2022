__lineNumber          = 0         # for lexer/parser
# if lexer and parser merged could be not so global
lineCounter         = 0         # for translator and jumps
variablesNames      = []        # usage Compilator, Parser, Translator
variablesNumbers    = ["1"]     # for adding to #Parser, Translator
variableInit        = []        # only in Parser, always with variablesNames
proceduresNames     = []        # only in Parser
instructions        = []        # in Parser, Translator, Compilator, but probably could be returned by Parser and be a parameter for translator