import sys
from tobiqLexer import TobiqLexer
from tobiqParser import TobiqParser
from tobiqTranslator import TobiqTranslator
import tobiqContext_ as global_
from tobiqExceptions import *

def main():

    lex = TobiqLexer()
    pars = TobiqParser()

    with open(sys.argv[1]) as in_f:
        text = in_f.read()

    try:
        instructions = pars.parse(lex.tokenize(text))

    # DEBUG
        if len(sys.argv) > 3: 
            print(global_.variablesNames)
            print(global_.proceduresNames)
            with open(sys.argv[3]+".log", 'w') as out_f:
                for line in instructions:
                    print(line, file=out_f)

        trans = TobiqTranslator()
        trans.translate(instructions)

        with open(sys.argv[2], 'w') as out_f:
            for line in trans.code:
                print(line, file=out_f)
                # print(line)      # for debug

    except InvalidArgumentsNumberException as e: # work on python 3.x
        print(str(e))
    except UndeclaredProcedureException as e:
        print(str(e))
    except UndeclaredVariableException as e:
        print(str(e))
    except SecondaryVariableDeclarationException as e:
        print(str(e))
    except UninitializedUsageException as e:
        print(str(e))

if __name__ == "__main__":
    main()