# proj3-anagrams
Vocabularly anagrams game for primary school English language learners (ELL)


## Overview of revisions

I used examples found in minijax.html and flask_minijax.py to change this anagram game from a game that served a new static page every game move to using ajax(ajaj) to maintain state of webpage by dynamically updating per keystroke.

## Authors 

Initial version by M Young; to be revised by CIS 322 students. 
Revised by: Nicholas Eskie 

## Known bugs

The start/stop scheme is not working.  Flask (or perhaps the virtual
environment) is creating two Unix processes running the application,
and I am capturing the process ID for only one of them.  Therefore
stop.sh manages to kill only one, leaving the other running.  At this
time I do not know a workaround.  It is necessary to kill the second
process manually.  Use 'ps | grep python' to discover it, then 'kill'
to kill it.  Or, on Linux systems, use the 'killall' command. 


## To run automated tests 
* `nosetests`

There are currently nose tests for vocab.py, letterbag.py, and jumble.py. 

'make test' should work.  To run 'nosetests' explicitly, you must be
in the 'vocab' subdirectory. 
