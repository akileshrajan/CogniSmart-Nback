# CogniSmart: A smat cognitive assessment system based on the N-back task.

### N-Back Working Memory Task
According to psytoolkit [1,2,3], N-Back working memory task is a task where you will see a sequence
of letters. Each letter is shown for a few seconds. You need to decide if you saw the same letter 3 trials ago, that is,
 in this case a n=3-back task.
<p>
In this application, we have implemented an N-back application with a visual stimuli and audio stimulti. The practitioners
can choose which stimulti they wish to use. The application has a total of 4 rounds, two rounds of the 0-back task and 
two rounds of 2-back task. Two rounds of each task is always presented together and the order of 0-back and 2-back will 
be counterbalanced amoung subjects. Each task has a total of 65 trials per round 16 of which are targets.
<p>
In our task, based on the implementation of the n-back task by PsyToolkit, the stimulti appears on the screen for 
2 seconds and a new stimuli is presented after 500 ms of each stimuli.

#### 0-Back Task
In this task, a predefined symbol is specified to the participants and this symbol wil be the target for the round.
The participants are required to press a button on the keyboard once they think they saw the symbol. This task doesnt 
require working memory but requires sustained attention [4].

#### 2-Back Task
In this task, the target is the symbol that appeared two trials back. The participants are required to press a button on
the keyboard when they think they saw the symbol.

### Sensors Used
1. Muse Headset.
2. Intel Realsense sensor
3. Fitbit Smart watches and Fitbit trackers.
4. BioSignal Plux - ECG sensor.

### Dependencies
1. Kivy Python Cross-Platform Gui library 1.9.0 or newer
2. Install Python SDK Tools: http://das.nasophon.de/pyliblo/ 

Note: Since we use 64-bit Linux OS, check the following link for MuseSDK on 64-bit system: http://forum.choosemuse.com/t/issues-running-muselab-and-muse-io/112/20 or https://github.com/elnn/tomato/blob/master/README.md


### References
[1] Stoet, G. (2010). PsyToolkit - A software package for programming psychological experiments using Linux. Behavior Research Methods, 42(4), 1096-1104. <br> 
[2] Stoet, G. (2017). PsyToolkit: A novel web-based method for running online questionnaires and reaction-time experiments. Teaching of Psychology, 44(1), 24-31. <br> 
[3] Jaeggi, S.M., Buschkuehl, M., Perrig, W.J., & Meier, B. (2010). The concurrent validity of the N-back task as a working memory measure. Memory, 18, , 394–412 <br> 
[4] Miller, K. M., Price, C. C., Okun, M. S., Montijo, H., & Bowers, D. (2009). Is the n-back task a valid neuropsychological measure for assessing working memory?. Archives of Clinical Neuropsychology, 24(7), 711-717. <br> 
