import sys
from tobiqLexer import MyLexer
from tobiqParser import MyParser
import tobiqContext_

def main():

    if len(sys.argv)!=3:
        print("io error")
        return

    lex = MyLexer()
    pars = MyParser()

    with open(sys.argv[1]) as in_f:
        text = in_f.read()

    pars.parse(lex.tokenize(text))

    print(tobiqContext_.instructions)
    print(tobiqContext_.variablesNames)
    print(tobiqContext_.proceduresNames)
    # code_gen = pars.code
    # code_gen.gen_code()
    
    # with open(sys.argv[2], 'w') as out_f:
    #     for line in pars:
    #     for line in code_gen.code:
    #         print(line, file=out_f)

main()