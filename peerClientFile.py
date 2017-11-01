from socket import *
from supportFile import *
from peerServerFile import *
import threading

class Peer_Client:

    #peer_client_port = 65433
    rfc_list_head = None
    file_path = None
    cwd = None

    def __init__(self):
        #initializing the values and taking user inputs
        cwd = os.getcwd()
        folder_name = input('Enter the rfc folder name\n')
        print('The rfc folder absolute path\n')
        Peer_Client.file_path = cwd + '\\' + folder_name
        print(Peer_Client.file_path)

        #creating a timing file
        f = open('timing' + str(Peer_Server.peer_server_port) +'.txt', 'wb')
        f.close()

        #Building the initial RFC list
        Peer_Client.rfc_list_head = RFC_Details.build_initial_rfc_list(Peer_Client.file_path, Peer_Server.peer_server_port)
        print('Initial RFC List')
        RFC_Details.print_rfc_list(Peer_Client.rfc_list_head)
        self.decrementTTL()

    #write data to file
    def receive_file(self, rfc_num, conn):
        file_name = Peer_Client.file_path + '\\' + 'rfc' + f'{rfc_num}'+'.txt'
        print(file_name)
        with open(file_name, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)
            f.close()

    #Operation
    def perform_operation(self, operation, addr, rfc_num=0):

        clientSocket = socket(AF_INET, SOCK_STREAM)
        #Binding not required
        #clientSocket.bind((gethostname(), Peer_Client.peer_client_port))
        clientSocket.connect(addr)

        #Based on operation build request
        if(operation == 'RFCQuery'):
            request_string = Request_builder.rfcQuery(Peer_Server.cookie_id)
        elif(operation == 'GetRFC'):
            request_string = Request_builder.getRfcFile(Peer_Server.cookie_id, rfc_num)
        else:
            return 'Invalid Operation'

        #Send request and receive response
        print(request_string)
        clientSocket.send(request_string.encode('utf-8'))
        response_string = clientSocket.recv(32768).decode('utf-8')
        print(response_string)

        #Based on operation parse response
        if(operation == 'RFCQuery'):
            rfc_data = Response_parser.rfcQuery_parse(response_string)
            new_rfc_list_head = RFC_Details.parse_string(rfc_data)
            Peer_Client.rfc_list_head = RFC_Details.mergeRFC(Peer_Client.rfc_list_head, new_rfc_list_head)
            RFC_Details.print_rfc_list(Peer_Client.rfc_list_head)
        elif(operation == 'GetRFC'):
            status = Response_parser.getRfcFile_parse(response_string)
            if(status == 'OK'):
                #receive file at this location
                self.receive_file(rfc_num, clientSocket)
                file_name = 'rfc' + rfc_num + '.txt'
                downloaded_rfc = RFC_Details()
                downloaded_rfc.rfc_entry(rfc_num, file_name , gethostbyname(gethostname()), Peer_Server.peer_server_port , 'Local' )
                Peer_Client.rfc_list_head = RFC_Details.add_next_node(Peer_Client.rfc_list_head, downloaded_rfc)

        else:
            return 'Invalid Operation'

        #Close connection
        clientSocket.close()

    #Method called by thread to decrement TTL value for ever minitue
    def decrementTTL(self):
        threading.Timer(60.0, self.decrementTTL).start()
        if (Peer_Client.rfc_list_head != None) :
            RFC_Details.decrement_ttl(Peer_Client.rfc_list_head)
