import sys
import threading
import time
import re
import datetime
from socket import *

#need 4 command line arguments
if len(sys.argv)<4:
    print('need 4 arguments')
    sys.exit()
serverName = sys.argv[1]                    #server_IP
serverPort = int(sys.argv[2])               #server_port
serverPort2 = int(sys.argv[3])              #client_udp_port
clientSocket = socket(AF_INET, SOCK_STREAM)

#upload to the server
def upload(clientsocket):
    with open('z5272202_contactlog.txt') as f:
        content=f.readlines()
        count=0
        for i in content:
            if len(i)>=19:
                count+=1
        clientsocket.sendall((str(count)).encode())
        clientsocket.recv(1024)
        for i in content:
            if len(i.rstrip())>=19:
                clientsocket.sendall(i.strip().encode())
                clientsocket.recv(1024)
                print(i.rstrip())

#communicate with server using tcp
def tcp(serverName,serverPort,clientSocket):
    try:
        clientSocket.connect((serverName, serverPort))
    except OSError:
        sys.exit()
    tempid = '0' #initialize tempid to 0
    # initialize starttime and expiretime
    starttime = datetime.datetime.now()
    expiretime = datetime.datetime.now()
    usersname=input('Username: ')
    clientSocket.sendall(usersname.encode())
    while True:
        password=input('Password: ')
        clientSocket.sendall(password.encode())
        message=clientSocket.recv(1024)
        print(message.decode())
        if message.decode()=='Your account is blocked due to multiple login failures. Please try again later':
            break
        elif message.decode()=="Welcome to the BlueTrace Simulator!":
            message=input("input the command: ")
            if message=='log out':
                clientSocket.send(message.encode())
            while message!='log out' :
                if message=='Download_tempID':
                    clientSocket.send(message.encode())
                    id = clientSocket.recv(1024)
                    tempid=id.decode()
                    starttime=datetime.datetime.now()
                    expiretime=starttime+datetime.timedelta(minutes=15)
                    print('TempID:\n'+id.decode())
                elif re.match('Beacon',message):
                    try:
                        l=message.split() #store ip and port number into a list
                        ipaddress=l[1]
                        port=int(l[2])
                        string_start=starttime.strftime("%d/%m/%Y %H:%M:%S")
                        string_expire=expiretime.strftime("%d/%m/%Y %H:%M:%S")
                        send_udp(ipaddress,port,tempid,string_start,string_expire)
                    except:
                        print("can't send the beacon")
                elif message=='Upload_contact_log':
                    clientSocket.sendall(message.encode())
                    clientSocket.recv(1024)
                    upload(clientSocket)
                else:
                    print('Error. Invalid command')
                message = input("input the command: ")
            clientSocket.sendall(message.encode())
            clientSocket.close()
            print("you have logged out")
            break

#delete after 3 minutes
def delete(tempid):
    time.sleep(180)
    with open('z5272202_contactlog.txt') as f:
        content=f.readlines()
        for i in range(len(content)):
            if content[i].rstrip()==tempid:
                for j in range(3):
                    del content[i]
                break
        temp=content.copy()
    with open('z5272202_contactlog.txt','w') as f:
        for i in temp:
            f.write(i)


#check if beacon is valid
def validate(l):
    starttime=datetime.datetime.strptime(l[1],"%d/%m/%Y %H:%M:%S")
    expiretime=datetime.datetime.strptime(l[2],"%d/%m/%Y %H:%M:%S")
    currenttime=datetime.datetime.now()
    if currenttime>starttime and currenttime <expiretime:
        print('The beacon is valid.')
        f=open('z5272202_contactlog.txt','a')
        for i in l:
            f.write(i+'\n')
        f.close()
        return True
    else:
        print('The beacon is invalid.')
        return False

#listening other clients sending beacon
def listen_udp(serverport):
    serversocket = socket(AF_INET, SOCK_DGRAM)
    try:
        serversocket.bind(('',serverport))
    except:
        print('this port is already used')
        sys.exit()
    l=[] #list to store the beacon information
    while True:
        message, clientaddress= serversocket.recvfrom(1024)
        if len(message.decode())>1:
            print(message.decode())
            if len(message.decode())==20:
                l.clear()
            l.append(message.decode())
            if len(l)==3:
                print('Current time is:\n'+datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                if validate(l):
                    threading.Thread(target=delete,args=(l[0],)).start()


#sending beacon to other clients
def send_udp(servername,serverport,tempid,starttime,expiretime):
    if not int(tempid):
        print('you do not have valid tempid')
        return
    clientsocket=socket(AF_INET, SOCK_DGRAM)
    message=tempid
    print(message)
    clientsocket.sendto(message.encode(),(servername,serverport))
    message=starttime
    print(message)
    clientsocket.sendto(message.encode(), (servername, serverport))
    message=expiretime
    print(message)
    clientsocket.sendto(message.encode(), (servername, serverport))
    message='1'                         #send BlueTrace protocol version
    clientsocket.sendto(message.encode(),(servername,serverport))
    clientsocket.close()

#one thread for tcp connection to the server, another one for listening to other clients using udp
threading.Thread(target=listen_udp,args=(serverPort2,)).start()
threading.Thread(target=tcp,args=(serverName,serverPort,clientSocket)).start()



