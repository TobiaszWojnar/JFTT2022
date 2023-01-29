# JFTT2022
## Tobiasz Wojnar

Aktualnie prawie działa.
Wymaga zaimplementowania szybszego mnożenia, dzielenia i modulo.

### run
```
    python3 tobiqCompilator.py [input_code_file] [output_code_file]
```

### TESTS
I cerated Unit Tests in folder myTests. 
* 1-19 without procedures
* 20+ procedures


### TODO:

* [x] Is all code generated?
* [X] pointers and not pointers
  * [x] Change parser to return also const as variable
  * [X] Do I need to init const remembered as variables?
  * [X] Does all code have good ADD/ADDI (probably)
  * [X] READ
  * [X] WRITE
  * [X] in procedures check if local or pointer
  * [X] EVAL VARIABLE in Translator
* [ ] ERROR handling
  * [X] Define custom exeptions 
  * [X] Detect InvalidArgumentsNumberException
  * [X] UndeclaredProcedureException
  * [X] UndeclaredVariableException
  * [X] SecondaryVariableDeclarationException
  * [X] UninitializedUsageException
  * [ ] Change Errors to wornings if raised in if's
* [X] JUMPS
  * [X] Create callback table
  * [X] Set all callbacks
  * [X] EVAL JUMPS in Translator
  * [X] Set jumps back to procedures
  * [ ] Debug
* Clean up:
  * [X] Comment output code with [begin inst], [end inst]
  * [X] Cleanup loops
* [X] Check if multi works
* [ ] EXTRA
  * [ ] Implement multi, div and mod as procedures at the beginning of document
  * [ ] Check if any multi, div, mod
  * [ ] Check if każda procedura występuje (while "w poprzednim kroku coś wywaliliśmy")
  * [ ] If więcej niż zero pracedur add Main jump