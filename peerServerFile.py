from socket import *
from supportFile import *

class Peer_Server:

    rs_port = 65423
    peer_server_port = None
    peer_list_head = None
    cookie_id = None
    rs_server_host_addr = None

    #Registration is done when client_server object is created
    def __init__(self):

        Peer_Server.rs_server_host_addr = input('Enter the RS server address\n')
        while True:
            p = input('Enter the port number between 65430 and 65500\n')
            if(int(p) > 65429  and int(p) < 65501):
                Peer_Server.peer_server_port = int(p)
                break

        clientSocket = socket(AF_INET, SOCK_STREAM)
        #clientSocket.bind((gethostname(), Peer_Server.peer_server_port))
        #clientSocket.connect((gethostname(), Peer_Server.rs_port))
        clientSocket.connect((str(Peer_Server.rs_server_host_addr).strip(), Peer_Server.rs_port))

        #Build and send request
        request_string = Request_builder.registration(Peer_Server.peer_server_port)
        print('Sent request:')
        print(request_string)
        clientSocket.send(request_string.encode('utf-8'))

        #Parse response_string
        response_string = clientSocket.recv(1024).decode('utf-8')
        self.cookie_id = Response_parser.registration_parse(response_string)
        Peer_Server.cookie_id = self.cookie_id
        print('Received response:')
        print(response_string)

        #Close connection
        clientSocket.close()

    #RS related other operations
    def perform_operation(self, operation):

        clientSocket = socket(AF_INET, SOCK_STREAM)
        #clientSocket.bind((gethostname(), Peer_Server.peer_server_port))
        #clientSocket.connect((gethostname(), Peer_Server.rs_port))
        clientSocket.connect((str(Peer_Server.rs_server_host_addr).strip(), Peer_Server.rs_port))

        #Based on operation build request
        if(operation == 'PQuery'):
            request_string = Request_builder.pQuery(self.cookie_id)
        elif(operation == 'Leave'):
            request_string = Request_builder.leave(self.cookie_id)
        elif(operation == 'KeepAlive'):
            request_string = Request_builder.keepAlive(self.cookie_id)
        elif(operation == 'Re_Register'):
            request_string = Request_builder.re_registration(gethostname(), self.cookie_id)
        else:
            return 'Invalid Operation'

        #Send request and receive response
        print(request_string)
        clientSocket.send(request_string.encode('utf-8'))
        response_string = clientSocket.recv(1024).decode('utf-8')
        print(response_string)

        #Based on operation parse response
        if(operation == 'PQuery'):
            peer_data = Response_parser.pQuery_parse(response_string)
            Peer_Server.peer_list_head = Peer_Details.parse_string(peer_data)
            Peer_Details.print_peer_list(Peer_Server.peer_list_head)
        elif(operation == 'Leave'):
            status = Response_parser.leave_parse(response_string)
        elif(operation == 'KeepAlive'):
            status = Response_parser.keepAlive_parse(response_string)
        elif(operation == 'Re_Register'):
            status = Response_parser.re_registration_parser(response_string)
        else:
            return 'Invalid Operation'

        #Close connection
        clientSocket.close()

#c = Peer_Server()
#c.perform_operation('PQuery')
#c.perform_operation('KeepAlive')
#c.perform_operation('Leave')
#c.perform_operation('Re_Register')
