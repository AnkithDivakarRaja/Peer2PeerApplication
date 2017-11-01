from socket import *
from supportFile import *
import threading

class RS_Server:

    peer_list_head = None

    def __init__(self):
        self.portNum = 65423
        self.decrementTTL()

    #Registration operation
    def registration(self):
        if (RS_Server.peer_list_head == None):
            head = Peer_Details()
            reg_cookie = head.first_entry(self.client_details[0], self.peer_server_port_num)
            RS_Server.peer_list_head = head
            #Peer_Details.list_head = head
            print('Head node of peer list:')
            Peer_Details.print_peer(RS_Server.peer_list_head)
        else:
            peer = Peer_Details()
            reg_cookie = peer.first_entry(self.client_details[0], self.peer_server_port_num)
            Peer_Details.add_next_node(RS_Server.peer_list_head, peer)
            print('Updated peer list:')
            Peer_Details.print_peer_list(RS_Server.peer_list_head)
        return Response_builder.registration('200', str(reg_cookie))

    #Peer List Request
    def get_peer_list(self):
        return Response_builder.pQuery('200', Peer_Details.pQuery_list(RS_Server.peer_list_head, self.request_cookie_id))

    #Leave Request
    def leave_request(self):
        Peer_Details.change_status(RS_Server.peer_list_head, self.request_cookie_id, False)
        print('Updated peer list:')
        Peer_Details.print_peer_list(RS_Server.peer_list_head)
        return Response_builder.leave('200')

    #KeepAlive Request
    def keepAlive_request(self):
        Peer_Details.change_status(RS_Server.peer_list_head, self.request_cookie_id, True)
        print('Updated peer list:')
        Peer_Details.print_peer_list(RS_Server.peer_list_head)
        return Response_builder.keepAlive('200')

    #Re-registration Request
    def re_registration(self):
        Peer_Details.update_registration(RS_Server.peer_list_head, self.request_cookie_id)
        print('Updated peer list:')
        Peer_Details.print_peer_list(RS_Server.peer_list_head)
        return Response_builder.re_registration('200')

    #Request method
    def operation(self, operation):
        if(operation == 'Register'):
            if self.request_cookie_id == None :
                return self.registration()
            else:
                return self.re_registration()
        elif(operation == 'PQuery'):
            return self.get_peer_list()
        elif(operation == 'Leave'):
            return self.leave_request()
        elif(operation == 'KeepAlive'):
            return self.keepAlive_request()
        else:
            return 'Invalid Request Operation'

    #Start regisrtation server
    def start_server(self):
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((gethostname(),self.portNum))
        serverSocket.listen(5)

        print ('Registration Server is ready to receive on ' + gethostbyname(gethostname()))
        while 1 :
            connectionSocket, addr = serverSocket.accept()
            self.client_details = addr

            #Receive request
            request = connectionSocket.recv(1024)
            print('Received request:\n' + request.decode('utf-8'))

            #Parse request
            operation = Request_parser.parse(request.decode('utf-8'))
            self.request_cookie_id = Request_parser.get_cookie_id(request.decode('utf-8'))
            self.peer_server_port_num = Request_parser.get_port_num(request.decode('utf-8'))

            #Operation
            response_string = self.operation(operation)
            print('Sent response:\n' + response_string)

            #Send response
            connectionSocket.send(response_string.encode('utf-8'))
            self.request_cookie_id = None
            connectionSocket.close()

    #Method called by thread to decrement TTL value for ever minitue
    def decrementTTL(self):
        threading.Timer(60.0, self.decrementTTL).start()
        if (RS_Server.peer_list_head != None) :
            Peer_Details.decrement_ttl(RS_Server.peer_list_head)


rs = RS_Server()
rs.start_server()
