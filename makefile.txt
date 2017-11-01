README

1)The program was developed and tested on Windows OS
2)The program was developed using python 3.6.3

Steps to start RS server:
1) supportFile.py and rsServerFile.py should be in the same folder location.
2) Run the file, rsServerFile.py 

Steps to start a peer:
1) supportFile.py, peerFile.py, peerClientFile.py and peerServerFile.py should be in the same folder location.
2) Run the file, peerFile.py
3) Enter the registration server IP address when prompted.
4) Enter the port number to which the peer server should be bound
5) Enter the folder name where the RFC files will be downloaded(folder should be present in the same location as the code)

Assumptions:
The code has been developed in a way that there is no requirement of user intervention and to achieve the same, we have used threading along with timers to trigger certain processes periodically.
1) PQuery is sent out every 60s (configurable) by each peer.
2) RFC query is sent to all other known peers(peers returned in PQuery) every 60s(configurable).
3) The peer keeps comparing the RFC list with the downloaded files and will request for missing files, if any every 1s(configurable).

Testing:
1) RS server and peers were tested with 60 latest RFC files(Filename: rfcXXXX.txt format)




