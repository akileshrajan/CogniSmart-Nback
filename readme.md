# CogniSmart: A smat cognitive assessment system based on the N-back task.

### Sensors Used
1. Muse Headset.
2. Intel Realsense sensor

### N-Back Working Memory Task
According to psytoolkit [1,2,3], N-Back working memory task is a task where you will see a sequence
of letters. Each letter is shown for a few seconds. You need to decide if you saw the same letter 3 trials ago, that is,
this is a n=3-back task.
<p>
If you saw the same letter three trials ago, you press a button provided according to the task requirements.
For example if you saw the letters A,B,L,T,B,C. You press a button when you see the letter B a second time since it 
appeard exactly 3 turns after it first appeared. 
<p>
In our task, based on the implementation of the n-back task by PsyToolkit, the stimulti appears on the screen for 
2 seconds and a new stimuli is presented after 500 ms of each stimuli.
<p>
The game has a total of 4 rounds, two rounds of the 0-back task and two rounds of 2-back task. Two rounds of each
task were always presented together and the order of 0-back and 2-back were counterbalanced amoung subjects. 
The task has a total of 65 trials per round 16 of which are targets.

[1] Stoet, G. (2010). PsyToolkit - A software package for programming psychological experiments using Linux. Behavior Research Methods, 42(4), 1096-1104. <br> 
[2] Stoet, G. (2017). PsyToolkit: A novel web-based method for running online questionnaires and reaction-time experiments. Teaching of Psychology, 44(1), 24-31. 
[3] Jaeggi, S.M., Buschkuehl, M., Perrig, W.J., & Meier, B. (2010). The concurrent validity of the N-back task as a working memory measure. Memory, 18, , 394–412
