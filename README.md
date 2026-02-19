# exam03Practice

User guide:

1. edit .bashrc or .zshrc (nano .bashrc), at the end of the file, add:

EXAM_PATH = "exam_manager.py path route"

alias exam_start="python3 $EXAM_PATH start"
alias exam_grade="python3 $EXAM_PATH grade"
alias exam_status="python3 $EXAM_PATH status"
alias exam_reset="python3 $EXAM_PATH reset"

2. open the repository directory.
3. execute exam_start (if you want to practice an specific subject, execute exam_start 'name_of_subject').
4. a random ( or not so random ;) ) subject will appear at the "rendu" directory.
5. you can check if the program detect your *.c file by executing exam_status.
6. When you are finished, grade your solution by executing exam_grade.
If you passed, a SUCCESS message will appear and another subject will be generated in the 'rendu' directory.
Otherwise, a FAIL message will appear, and you will be stuck some more time with the same subject.
7. You can remove everything you have done in your actual subject by executing exam_reset. 
