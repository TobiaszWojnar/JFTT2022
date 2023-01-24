# JFTT2022
## Tobiasz Wojnar

Aktualnie nie działa - czesć instrukcji nie jest jeszcze tłumaczona, nie poprawiam wskaźników na zimenne/skoki.

### run
```
    python3 tobiqCompilator.py [input_code_file] [output_code_file]
```

### TODO:
* [x] Is all code generated?
* [ ] pointers and not pointers
  * [x] Change parser to return also const as variable
  * [ ] Do I need to init them?
  * [X] Does all code have good ADD/ADDI (probably)
  * [ ] READ (no idea)
  * [X] WRITE
  * [ ] in procedures check if local or pointer
  * [X] EVAL VARIABLE in Translator
* [ ] JUMPS
  * [ ] EVAL JUMPS in Translator
* [ ] Comment output code with [begin inst], [end inst]
* [ ] Check if multi works
* [ ] EXTRA
  * [ ] Check if any multi, div, mod
  * [ ] Check if każda procedura występuje (while "w poprzednim kroku coś wywaliliśmy")
  * [ ] If więcej niż zero pracedur add Main jump