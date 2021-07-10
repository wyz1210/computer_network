# computer_network
Program Design
1.	Clients use usersname and password to log in the server. If clients input 3 wrong password consecutively, it will be blocked for a certain time ( decided by server).
2.	Clients can ask for tempid. The server will generate a new random number for each client every time. The number is 20 bytes. Server will also store this tempid and start time, expire time into “tempIDs.txt”. 
3.	Clients can send beacons to each other. And the client receive the beacon will check it and store the valid beacon into “z5272202_contactlog.txt” for 3 minutes.( Beacon is deleted after 3 minutes automatically). 
4.	Clients can upload contact log( containing tempid, starttime and expire time) to the server, and the server will print phone numbers and time information according to tempid. 
5.	Clients can log out at any time after logging in.
Instruction:
1.	I am using python 3. If it is run in VLAB, users should type “python3 server.py...” 
First open server.py by typing: python server.py server_port block_duration
Like ( python server.py 13000 60)
Then open client.py by typing: python client.py server_IP server_port client_udp_port
Like ( python client.py 127.0.0.1 13000 14000)
(Both are exactly the same with ass.pdf)

2.	Once the server.py is opened. It will print “I am listening”
 
The client.py will prompt users for username and password step by step. If success it will be like this and ask for commands:
 
If it fails or fails for 3 times it will be like just the same as that in the ass.pdf.

3.	Users should type “Download_tempID” to get tempid. The client will show like below:

 
The server will show the same information as that in ass.pdf.

4.	Clients should type “Beacon <dest IP> <dest port>” to send beacons like below
 
And the client at the other side will be like below:
 
Note that the information showed at the other client will take up the space of the input, but this user can still input command at the last blank line. 

5.	Users should type command “Upload_contact_log” to upload to the server
 
And the server will show the corresponding information. But after checking the contact log, the server will print not only the phone number and the start time but also the expire time like below: 
 

Beacon
1.	The beacon format is “TempID (20 bytes), start time (19 bytes), expiry time (19 bytes) and BlueTrace protocol version (1 byte)”
The client will send them one by one to the other client.
TempID is the random generated number, while start time and expiry time format is “"%d/%m/%Y %H:%M:%S". For example: ” 30/07/2020 16:58:12”.
The BlueTrace protocol version is ‘1’. I just send it to the other client but without print it and store it.
2.	After receiving the beacon, if it is valid, the client will store the TempID (20 bytes), start time (19 bytes) and expiry time (19 bytes) into “z5272202_contactlog.txt”. After 3 min, this information will be deleted. If the beacon is invalid, the client will print “the beacon is invalid”.
3.	The “z5272202_contactlog.txt” has a little different format. Each beacon takes 3 lines like below: (tempid, start time and expire time respectively) 
 
Others
1.	If the client send beacon to other client before downloading tempid from server, it will print “you do not have valid tempid”.
2.	Clients can only use 4 commands after logging in : “Download_tempID” , “Upload_contact_log” , “Beacon <dest IP> <dest port>” and “log out”. 
For other commands the program will print “Error. Invalid command”. If the beacon command has a wrong format, it will print “"can't send the beacon".
3.	For updating the contact log, clients will send one packet for one tempid, one packet   for start time, and one packet for expire time. When the server receive each packet from a client, it will send a ‘1’ to the client.
4.	After the client input “log out”, it can no longer communicate to the server. But it can still listen to other clients sending beacon and print information.(TCP is disconnected but UDP is still ok).
