DCASE2020 - Task 1 - Submission validator
-----------------------------------------

Author:

**Toni Heittola**, *Tampere University* 
[Email](mailto:toni.heittola@tuni.fi), 
[Homepage](http://www.cs.tut.fi/~heittolt/), 
[GitHub](https://github.com/toni-heittola)

This is an automatic validation tool for [DCASE2020 Challenge task1](http://dcase.community/challenge2020/task-acoustic-scene-classification) submission. 
The tool helps challenge participants to prepare correctly formatted submission packages, 
which in turn will speed up the submission processing in the challenge evaluation stage.

Files are validated as strictly as possible against [submission instructions](http://dcase.community/challenge2020/task-acoustic-scene-classification#submission). 
However, it is quite tricky to take into account all possible error combinations. 
So if you get a validation error, but you feel that formatting is in fact correct, 
just proceed with submission.

Validator is made for Python version >= 3.7.  
   
## Usage

To validate full submission **package** (in ZIP format):

    python main.py -p submission_package.zip

To validate **single entry** (a pair of system output and associated meta information files) for subtask A (Acoustic Scene Classification with Multiple Devices ):
   
     python main.py -t A -o Test_TAU_task1a_1.output.csv -m Test_TAU_task1a_1.meta.yaml
  
And same for subtask B (Low-Complexity Acoustic Scene Classification):  
    
    python main.py -t B -o Test_TAU_task1b_1.output.csv -m Test_TAU_task1b_1.meta.yaml
    
