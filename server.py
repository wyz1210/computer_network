#using python 3
import sys
import _thread
from socket import *
import time
import datetime
import random
import re

#check if password is correct
def check(usersname,password):
    with open ("credentials.txt") as f:
        content=f.readlines()
        l=[]
        for i in content:
            l.append(i.split())
        for i in range(len(l)):
            if l[i][0]==usersname:
                return (password==l[i][1])
        return False

#check if the user is blocked
def check_block(username,clientsocket):
    if username.decode() in block_users:
        clientsocket.send("Your account is blocked due to multiple login failures. Please try again later".encode())
        clientsocket.close()
        return False
    return True

#generate the tempid
def generate_tempid(username,clientsocket):
    #write tempid, starttime , expiretime into tempIDs.txt file
    with open ("tempIDs.txt",'a') as f:
        f.write(username.decode()+' ')
        tempid=random.randint(10000000000000000000,99999999999999999999)
        print('TempID:\n' + str(tempid))
        clientsocket.send(str(tempid).encode())
        f.write(str(tempid)+' ')
        starttime = datetime.datetime.now()
        expiretime = starttime+datetime.timedelta(minutes=15)
        sting_of_starttime = starttime.strftime("%d/%m/%Y %H:%M:%S")
        string_of_expiretime = expiretime.strftime("%d/%m/%Y %H:%M:%S")
        f.write(sting_of_starttime+' ')
        f.write(string_of_expiretime+' ')
        f.write('\n')


#map the TempID to reveal the UserID and retrieve start time and expiry time
def retrieve(l):
    print('Contact log checking')
    list=[] #store tempids.txt content
    with open('tempIDs.txt') as file:
        content=file.readlines()
        for i in content:
            list.append(i.split())
        for i in l:
            for j in list:
                if j[1]==i:
                    print(j[0])
                    print(j[2]+' '+j[3])
                    print(j[4]+' '+j[5])



#get command after user logs in
def command(clientsocket,username):
    message=clientsocket.recv(1024)
    while(message.decode()!='log out'):                         #if command is not log out, keep going
        if message.decode()=='Download_tempID':                 #download tempid command
            generate_tempid(username, clientsocket)             #generate tempid , write tempid.txt
                                                                # and send tempid to users

        elif message.decode()=='Upload_contact_log':            #upload contact log id
            print('received contact log from '+username.decode())
            clientsocket.send('1'.encode())
            count1=clientsocket.recv(1024)
            clientsocket.send('1'.encode())
            count=int(count1.decode())
            list_of_tempid=[]
            for i in range(count):
                content = clientsocket.recv(1024)
                clientsocket.send('1'.encode())
                print(content.decode())
                if len(content.decode())==20:
                    list_of_tempid.append(content.decode())
            retrieve(list_of_tempid)                            #using temp.txt file to get phonenumber
        message = clientsocket.recv(1024)


#authentication
def log_in(connectionSocket,block_time):
    try:
        i=0
        usersname = connectionSocket.recv(1024)             # recieve usersname
        password = connectionSocket.recv(1024)              # recieve password
        if check_block(usersname,connectionSocket):             # check if the client is blocked
            for i in range(0,3):
                # using credentials.txt to authenticate clients
                if check(usersname.decode(),password.decode()):
                    connectionSocket.send("Welcome to the BlueTrace Simulator!".encode())
                    print('users: '+usersname.decode())
                    command(connectionSocket,usersname)
                    print(usersname.decode() + ' logout')
                    break
                else:
                    if i!=2:
                        connectionSocket.send("Invalid Password. Please try again".encode())
                    #3 consecutive wrong password
                    if i == 2:
                        connectionSocket.send(
                        "Your account is blocked due to multiple login failures. Please try again later".encode())
                        break
                password = connectionSocket.recv(1024)         # recieve password
            connectionSocket.close()
            #if users input 3 consecutive wrong password, put them in the block_user list.
            if i==2:
                block_users.append(usersname.decode())
                time.sleep(block_time)
                block_users.remove(usersname.decode())
    except:
        return

#need 3 command line arguments
if len(sys.argv)<3:
    print('need 2 arguments')
    sys.exit()
serverPort = int(sys.argv[1])  #server port
block_time = int(sys.argv[2])  #block_duration
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(5)
print("i am listening")
global block_users
block_users=[]
while True:
    connectionSocket, address = serverSocket.accept()
    _thread.start_new_thread(log_in,(connectionSocket,block_time))




