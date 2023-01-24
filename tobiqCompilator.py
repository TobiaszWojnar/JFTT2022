import sys
from tobiqLexer import TobiqLexer
from tobiqParser import TobiqParser
from tobiqTranslator import TobiqTranslator
import tobiqContext_ as global_

def main():

    # if len(sys.argv)!=3:
    #     print("io error")
    #     return

    lex = TobiqLexer()
    pars = TobiqParser()

    with open(sys.argv[1]) as in_f:
        text = in_f.read()

    pars.parse(lex.tokenize(text))

    print(global_.instructions)
    print(global_.variablesNames)
    print(global_.proceduresNames)

    with open(sys.argv[2]+".log", 'w') as out_f:
        for line in global_.instructions:
            print(line, file=out_f)

    trans = TobiqTranslator()
    trans.translate()

    with open(sys.argv[2], 'w') as out_f:
        for line in trans.code:
            print(line, file=out_f)
            print(line)      
    
    # with open(sys.argv[2], 'w') as out_f:
    #     for line in pars:
    #     for line in code_gen.code:
    #         print(line, file=out_f)

if __name__ == "__main__":
    main()