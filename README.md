This program serves as a speaker recognition software that can identify whether someone is speaking and the current speaker in run-time. 

How to use it:

0. install the following packages on the client side:
   	pip install socket
   	pip install sounddevice

  install PyTorch and the following packages on the server side:
  	pip install speechbrain
   	pip install socket

1. To set up server connection, follow these steps:
    1. Use regular ssh to connect to the Linux box. 
	    ssh zdai2@130.215.182.227
    2. Activate conda, and then run "python server.py"
	    conda activate speechbrain
	    python3 server.py
    3. On Windows terminal, use "ssh -L..." to open a SSH tunnel
	    ssh -L 12345:localhost:12345 zdai2@130.215.182.227 -N

2. To start the program, run user_interface.py
    In the "enrollment" page, user can type in the name of the speaker and talk to save a 5 second voice sample to server for later identification.

    In the "recognition" page, the program will load the sample audio and display who the speaker was every second once the recognition button is pressed
