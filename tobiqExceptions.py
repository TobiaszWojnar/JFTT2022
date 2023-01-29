class InvalidArgumentsNumberException(Exception):

    def __init__(self, procName, args, line, message="ERROR. Wrong number of arguments "):
        super().__init__(message+" "+procName+" "+str(args)+" in line "+ str(line))

class UndeclaredProcedureException(Exception):

    def __init__(self, procName, line, message="ERROR. Undeclared Procedure "):
        super().__init__(message+" "+procName+" in line "+ str(line))

class UndeclaredVariableException(Exception):

    def __init__(self, varName, line, message="ERROR. Undeclared variable = "):
        super().__init__(message+" "+varName+" in line "+ str(line))

class SecondaryVariableDeclarationException(Exception):

    def __init__(self, variables, procName, message="ERROR. Secondary variable declaration = "):
        super().__init__(message+" "+str(variables)+" in procedure "+ procName)

class UninitializedUsageException(Exception):

    def __init__(self, varName, line, message="ERROR. Uninitialized Usage = "):
        super().__init__(message+" "+varName+" in line "+ str(line))