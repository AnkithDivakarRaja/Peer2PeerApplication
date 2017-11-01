from socket import *
from supportFile import *
import threading
import os
from peerServerFile import *
from peerClientFile import *
from datetime import datetime
import sys
sys.setrecursionlimit(1500)

class Peer:

    server = None
    client = None
    total_download_time = datetime.now() - datetime.now()
    total_file_download_time = datetime.now() - datetime.now()

    def __init__(self):
        Peer.server = Peer_Server()
        self.get_Peer_List()
        Peer.client = Peer_Client()
        self.connect_other_peer()
        self.download_start = datetime.now()
        self.request_file_peer()

    def get_Peer_List(self):
        threading.Timer(60.0, self.get_Peer_List).start()
        Peer.server.perform_operation('PQuery')
        Peer.server.perform_operation('KeepAlive')
        Peer.server.perform_operation('Leave')
        Peer.server.perform_operation('Re_Register')

    #Verify if file exisits
    def verfiy_file_presence(self, rfc_num):
        file_name = 'rfc' + f'{rfc_num}' + '.txt'
        #print(file_name)
        for file in os.listdir(Peer_Client.file_path):
            if file == (file_name) :
                return True
        return False

    #Send File to client
    def send_file(self, rfc_num, conn):
        file_name = Peer_Client.file_path + '\\' + 'rfc' + f'{rfc_num}' + '.txt'
        f = open(file_name,'rb')
        l = f.read(1024)
        while (l):
            conn.send(l)
            #print('Sent ',repr(l))
            l = f.read(1024)
        f.close()


    #Request method
    def operation(self, operation):
        if(operation == 'RFCQuery'):
            return Response_builder.rfcQuery('200', RFC_Details.rfcQuery_list(Peer_Client.rfc_list_head))
        elif(operation == 'GetRFC'):
            #Check if File exists
            self.file_transfer_status = self.verfiy_file_presence(self.request_rfc_num)
            if (self.file_transfer_status):
                return Response_builder.getRfcFile('200')
            else:
                return Response_builder.getRfcFile('404')
        else:
            return 'Invalid Request Operation'

    def connect_other_peer(self):
        threading.Timer(60.0, self.connect_other_peer).start()
        head = Peer_Server.peer_list_head
        while (head != None):
            Peer.client.perform_operation('RFCQuery', (head.host_name, int(head.port_num)))
            head = head.next

    def request_file_peer(self):
        threading.Timer(1.0, self.request_file_peer).start()
        next_file_request = RFC_Details.get_rfc_list_to_download(Peer_Client.rfc_list_head, Peer_Client.file_path)
        if (next_file_request != None):
            start_time = datetime.now()

            #Requesting RFC File
            Peer.client.perform_operation('GetRFC', (str(next_file_request.host_name).strip() , int(next_file_request.port_num)), next_file_request.rfc_num )

            #write timing data to file
            end_time = datetime.now()
            self.download_end = datetime.now()
            Peer.total_file_download_time = Peer.total_file_download_time + (end_time - start_time)
            Peer.total_download_time = self.download_end - self.download_start
            f = open('timing' + str(Peer_Server.peer_server_port) +'.txt', 'a')
            f.write('RFC ' + str(next_file_request.rfc_num) + ' Downloaded from: ' + str(next_file_request.host_name).strip() + ':' + str(next_file_request.port_num).strip() + '\n')
            f.write('Total time to download just the files: ')
            f.write(str(Peer.total_file_download_time))
            f.write('\n')
            f.write('Total time since start to finish downloading all files: ')
            f.write(str(Peer.total_download_time))
            f.write('\n\n')
            f.close()


    def server_thread_operation(self, name, connectionSocket, addr):
        self.client_details = addr

        #Receive request
        request = connectionSocket.recv(32768)
        print('Received request:\n' + request.decode('utf-8'))

        #Parse request
        operation = Request_parser.parse(request.decode('utf-8'))
        self.request_cookie_id = Request_parser.get_cookie_id(request.decode('utf-8'))
        self.request_rfc_num = Request_parser.get_rfc_num(request.decode('utf-8'))

        #Operation
        response_string = self.operation(operation)
        print('Sent response:\n' + response_string)

        #Send response
        connectionSocket.send(response_string.encode('utf-8'))
        #Send File at this location
        if (self.file_transfer_status):
            #Send file here
            self.send_file(self.request_rfc_num, connectionSocket)

        self.request_cookie_id = None
        connectionSocket.close()

    def start_peer(self):
        self.file_transfer_status = False
        peerServerSocket = socket(AF_INET, SOCK_STREAM)
        peerServerSocket.bind((gethostname(), Peer_Server.peer_server_port))
        peerServerSocket.listen(5)
        print ('Peer is up and listining')
        while 1 :
            connectionSocket, addr = peerServerSocket.accept()

            print ("client connedted ip:<" + str(addr) + ">")
            t = threading.Thread(target=self.server_thread_operation, args=("RetrThread", connectionSocket, addr))
            t.start()

        peerServerSocket.close()

peer = Peer()
peer.start_peer()
