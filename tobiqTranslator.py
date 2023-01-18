import tobiqContext_

line_num = 63 #zaczynamy od 62 bo w pierwszej linijce zawsze będzie skok do main'a, a kolejne to library
location = None

class Translator:
    code = []

    def generate_code(self,lista):
        global line_num
        self.code.append("JUMPI " + str(tobiqContext_.variablesNames.index("ma1n 1ump")))
        Translator.generate_ready_library(self)
        Translator.generate_inner_code(self, lista)
        self.code.append("HALT")

    def generate_ready_library(self):
        #Equal evaluation
        self.code.append("SET 1")
        self.code.append("ADD 3")
        self.code.append("SUB 4")
        self.code.append("JPOS 6")
        self.code.append("JUMPI i")
        self.code.append("SUB 1")
        self.code.append("JZERO 9")
        self.code.append("JUMPI i")
        self.code.append("JUMPI 2")
        #Not Equal evaluation
        self.code.append("SET 1")
        self.code.append("ADD 3")
        self.code.append("SUB 4")
        self.code.append("JZERO 16")
        self.code.append("SUB 1")
        self.code.append("JPOS i")
        self.code.append("JUMPI 2")
        #Greater evaluation
        self.code.append("LOAD 3")
        self.code.append("SUB 4")
        self.code.append("JPOS 21")
        self.code.append("JUMPI i")
        self.code.append("JUMPI 2")
        #Greater/Equal evaluation
        self.code.append("SET 1")
        self.code.append("ADD 3")
        self.code.append("SUB 4")
        self.code.append("JPOS 27")
        self.code.append("JUMPI i")
        self.code.append("JUMPI 2")
        #Multiplication
        self.code.append("LOAD 4")
        self.code.append("STORE 6")
        self.code.append("STORE 7")
        self.code.append("SET 1")
        self.code.append("STORE 4")
        self.code.append("SET 36")
        self.code.append("STORE 2")
        self.code.append("JUMP 17")
        self.code.append("LOAD 6")
        self.code.append("ADD 7")
        self.code.append("STORE 6")
        self.code.append("LOAD 4")
        self.code.append("ADD 1")
        self.code.append("JUMP 17")
        #Division
        self.code.append("SET 1")
        self.code.append("SUB 1")
        self.code.append("STORE 6")
        self.code.append("SET 48")
        self.code.append("STORE 2")
        self.code.append("JUMP 22")
        self.code.append("LOAD 3")
        self.code.append("SUB 4")
        self.code.append("STORE 3")
        self.code.append("LOAD 6")
        self.code.append("ADD 1")
        self.code.append("STORE 6")
        self.code.append("JUMP 22")
        #Modulo
        self.code.append("LOAD 58")
        self.code.append("STORE 2")
        self.code.append("JUMP 22")
        self.code.append("LOAD 3")
        self.code.append("SUB 4")
        self.code.append("STORE 3")
        self.code.append("JUMP 22")

    def generate_inner_code(self, lista):
        global line_num
        global location
        for block in lista:
            for inst in block:
                if block[0] == 'PROCEDURE':
                    location = block[1]
                    self.code.append("SET " + str(line_num+3))
                    self.code.append("STORE " + str(tobiqContext_.variablesNames.index(str(location)+" 1ump")))
                    line_num += 2
                    Translator.generate_inner_code(self, inst)
                elif block[0] == 'PROGRAM':
                    location = "ma1n"
                    self.code.append("SET " + str(line_num+3))
                    self.code.append("STORE " + str(tobiqContext_.variablesNames.index("ma1n 1ump")))
                    line_num += 2
                    Translator.generate_inner_code(self, inst)
                elif block[0] == 'PROC':
                    location = block[1]
                    self.code.append("SET " + str(line_num+4))
                    self.code.append("STORE 2")
                    self.code.append("JUMPI " + str(tobiqContext_.variablesNames.index(str(block[1]) + " 1ump")))
                    line_num += 3
                    Translator.generate_inner_code(self, block)
                elif block[0] == 'READ':
                    self.code.append("GET " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    line_num += 1
                    Translator.generate_inner_code(self, inst)
                elif block[0] == 'WRITE':
                    self.code.append("PUT " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    line_num += 1
                    Translator.generate_inner_code(self, inst)
                elif block[0] == 'ASSIGN':
                    Translator.generate_inner_code(self, inst)
                    self.code.append("STORE " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    line_num += 1
                elif block[0] == 'add':
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("ADD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    line_num += 2
                elif block[0] == 'sub':
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("SUB " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    line_num += 2
                elif block[0] == 'mul':
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("STORE 3")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    self.code.append("STORE 4")
                    self.code.append("SET " + str(line_num+8))
                    self.code.append("STORE 2")
                    self.code.append("JUMP 28")
                    line_num += 7
                elif block[0] =='div':
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("STORE 3")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    self.code.append("STORE 4")
                    self.code.append("SET " + str(line_num+8))
                    self.code.append("STORE 2")
                    self.code.append("JUMP 42")
                    line_num += 7 
                elif block[0] == 'mod':
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("STORE 3")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    self.code.append("STORE 4")
                    self.code.append("SET " + str(line_num+8))
                    self.code.append("STORE 2")
                    self.code.append("JUMP 55")
                    line_num += 7
                elif block[0] == 'eq':
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("STORE 3")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    self.code.append("STORE 4")
                    self.code.append("SET " + str(line_num+8))
                    self.code.append("STORE 2")
                    self.code.append("JUMP 1")
                    line_num += 7           
                elif block[0] == 'neq':
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("STORE 3")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    self.code.append("STORE 4")
                    self.code.append("SET " + str(line_num+8))
                    self.code.append("STORE 2")
                    self.code.append("JUMP 10")
                    line_num += 7  
                elif block[0] == 'gr':
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("STORE 3")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    self.code.append("STORE 4")
                    self.code.append("SET " + str(line_num+8))
                    self.code.append("STORE 2")
                    self.code.append("JUMP 17")
                    line_num += 7 
                elif block[0] == 'geq':
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("STORE 3")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    self.code.append("STORE 4")
                    self.code.append("SET " + str(line_num+8))
                    self.code.append("STORE 2")
                    self.code.append("JUMP 22")
                    line_num += 7 
                elif block[0] == 'WHILE':
                    self.code.append("SET "+ str(line_num + 8))
                    self.code.append("STORE 2")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("STORE 3")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    self.code.append("STORE 4")
                    Translator.generate_inner_code(self, block)
                    self.code.append("SET "+ str(line_num + 10))
                    self.code.append("STORE 2")
                    Translator.generate_inner_code(self, block)
                    self.code.append("JUMP " + str(line_num + 7))
                    line_num += 9
                elif block[0] == 'IF':
                    self.code.append("SET "+ str(line_num + 7))
                    self.code.append("STORE 2")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[1]))))
                    self.code.append("STORE 3")
                    self.code.append("LOAD " + str(tobiqContext_.variablesNames.index(str(location) + str(block[2]))))
                    self.code.append("STORE 4")
                    Translator.generate_inner_code(self, inst) #alternatywnie swich case dla expressions
                    # Translator.generate_inner_code(self, inst)
