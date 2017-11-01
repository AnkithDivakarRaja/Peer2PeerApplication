from datetime import datetime
import copy
import os
from socket import *

class Peer_Details:

    #list_head = None
    cookie_num = 10000

    def __init__(self):
        self.ttl = 7200
        self.status = True
        self.num_reg_past_30_days = 0
        self.next = None

    def first_entry(self, host_name, port_num):
        self.host_name = host_name
        self.port_num = port_num
        Peer_Details.cookie_num += 1
        self.cookie_id = Peer_Details.cookie_num
        self.recent_reg_time = datetime.now()
        return self.cookie_id

    @classmethod
    def add_next_node(cls, head, new_peer):
        if (head.next != None):
            Peer_Details.add_next_node(head.next, new_peer)
        else:
            head.next = new_peer
        return head

    @classmethod
    def print_peer(cls, peer):
        print(f'Node details: {peer.cookie_id}, {peer.host_name}, {peer.port_num}, {peer.status}, {peer.ttl}, {peer.num_reg_past_30_days}, {peer.recent_reg_time}')

    @classmethod
    def print_peer_list(cls, head):
        if (head):
            Peer_Details.print_peer(head)
            Peer_Details.print_peer_list(head.next)

    @classmethod
    def pQuery_list(cls, head, cookie_id):
        peer_list = ''
        peer = head
        print(cookie_id)
        while True:
            #Add only active peers to the list
            if (peer.status & (str(peer.cookie_id) != str(cookie_id))):
                peer_list = peer_list + f'{peer.host_name}, {peer.port_num}' + '\r\n'
            #Check if next peer is present
            if (peer.next != None):
                peer = peer.next
            else:
                return peer_list

    @classmethod
    def change_status(cls, head, cookie_id, status):
        peer = head
        while True:
            if(int(peer.cookie_id) != int(cookie_id)):
                peer = peer.next
            else:
                peer.status = status
                if status:
                    peer.ttl = 7200
                else:
                    peer.ttl = 0
                return

    @classmethod
    def update_registration(cls, head, cookie_id):
        peer = head
        while True:
            if(int(peer.cookie_id) != int(cookie_id)):
                peer = peer.next
            else:
                peer.ttl = 7200
                peer.recent_reg_time = datetime.now()
                peer.num_reg_past_30_days = peer.num_reg_past_30_days + 1
                peer.status = True
                return

    @classmethod
    def decrement_ttl(cls, head):
        peer = head
        while True:
            peer = Peer_Details.decrement_ttl_peer(peer)
            if(peer == None):
                break

    @classmethod
    def decrement_ttl_peer(cls, peer):
        if (peer.ttl > 1):
            peer.ttl -= 1
        else:
            peer.ttl = 0
            peer.status = False
        return peer.next

    #Not tested yet
    @classmethod
    def parse_string(cls, data_string):
        data_string = data_string.splitlines()
        head_location = None
        for data in data_string:
            data = data.split(',')
            head = Peer_Details()
            head.first_entry(data[0], data[1])
            if head_location == None :
                head_location = head
            else:
                head_location = Peer_Details.add_next_node(head_location, head)
        return head_location

class RFC_Details:

    def rfc_entry(self, rfc_num, rfc_title, host_name, port_num, location):
        self.rfc_num = rfc_num
        self.rfc_title = rfc_title
        self.host_name = host_name
        self.port_num = port_num
        self.ttl = 7200
        self.location = location
        self.status = True
        self.next = None

    @classmethod
    def add_next_node(cls, head, new_rfc):
        new_head = head
        if head.rfc_num >= new_rfc.rfc_num :
            new_head = new_rfc
            new_head.next = head
        else:
            if head.next == None :
                new_rfc.next = None
                head.next = new_rfc

            elif head.next.rfc_num >= new_rfc.rfc_num :
                temp = head.next
                head.next = new_rfc
                new_rfc.next = temp
            else:
                RFC_Details.add_next_node(head.next, new_rfc)
        return new_head

    @classmethod
    def print_rfc(cls, rfc):
        print(f'RFC details: {rfc.rfc_num}, {rfc.rfc_title}, {rfc.host_name}, {rfc.port_num}, {rfc.ttl}, {rfc.location}, {rfc.status}')

    @classmethod
    def print_rfc_list(cls, head):
        if (head):
            RFC_Details.print_rfc(head)
            RFC_Details.print_rfc_list(head.next)

    @classmethod
    def rfcQuery_list(cls, head):
        rfc_list = ''
        rfc = head
        while True:
            #Add only active rfc to the list
            if (rfc.status):
                rfc_list = rfc_list + f'{rfc.rfc_num}, {rfc.rfc_title}, {rfc.host_name}, {rfc.port_num}' + ', Remote' + '\r\n'
            #Check if next peer is present
            if (rfc.next != None):
                rfc = rfc.next
            else:
                return rfc_list

    @classmethod
    def mergeRFC(cls, head, new_rfc_list_head):
        new_head = head
        while True:
            if(head == None):
                new_head = RFC_Details()
                peer = copy.deepcopy(new_rfc_list_head)
                new_head.rfc_entry(peer.rfc_num, peer.rfc_title, peer.host_name, peer.port_num, 'Remote')
                return new_head
            if(new_rfc_list_head != None):
                if(not(RFC_Details.isDuplicateEntry(new_head, new_rfc_list_head.rfc_num, new_rfc_list_head.host_name, new_rfc_list_head.port_num))):
                    new_head = RFC_Details.add_next_node(new_head, copy.deepcopy(new_rfc_list_head))
                new_rfc_list_head = new_rfc_list_head.next
            else:
                return new_head

    @classmethod
    def isDuplicateEntry(cls, head, rfc_num, host_name, port_num):
        rfc = head
        while True:
            if((str(rfc.rfc_num) == str(rfc_num)) and (str(rfc.host_name).strip() == str(host_name).strip()) and (str(rfc.port_num).strip() == str(port_num).strip())):
                return True
            #Check if next peer is present
            if (rfc.next != None):
                rfc = rfc.next
            else:
                return False

    @classmethod
    def decrement_ttl(cls, head):
        rfc = head
        while True:
            if(rfc.location == 'Remote'):
                rfc = RFC_Details.decrement_ttl_rfc(rfc)
            else:
                rfc = rfc.next
            if(rfc == None):
                break

    @classmethod
    def decrement_ttl_rfc(cls, rfc):
        if (rfc.ttl > 1):
            rfc.ttl -= 1
        else:
            rfc.ttl = 0
            rfc.status = False
        return rfc.next

    @classmethod
    def parse_string(cls, rfc_string):
        rfc_string = rfc_string.splitlines()
        rfc_head_location = None
        for rfc in rfc_string:
            rfc = rfc.split(',')
            head = RFC_Details()
            head.rfc_entry(rfc[0], rfc[1], rfc[2], rfc[3], rfc[4])
            if rfc_head_location == None :
                rfc_head_location = head
            else:
                rfc_head_location = RFC_Details.add_next_node(rfc_head_location, head)
        return rfc_head_location

    @classmethod
    def build_initial_rfc_list(cls, path, port_num):
        head_location = None
        for file in os.listdir(path):
            if file.endswith(".txt"):
                file_description = file
                file = file.split('rfc')
                file = file[1].split('.')
                if head_location == None :
                    head = RFC_Details()
                    head.rfc_entry(file[0], file_description, gethostbyname(gethostname()), str(port_num), 'Local')
                    head_location = head
                else:
                    rfc = RFC_Details()
                    rfc.rfc_entry(file[0], file_description, gethostbyname(gethostname()), str(port_num), 'Local')
                    head_location = RFC_Details.add_next_node(head_location, rfc)
        return head_location

    @classmethod
    def rfc_downloaded(cls, rfc_num, path):
        file_name = 'rfc' + f'{rfc_num}' + '.txt'
        #print(file_name)
        for file in os.listdir(path):
            if file == (file_name) :
                return True
        return False

    @classmethod
    def get_rfc_list_to_download(cls, head, path):
        peer = head
        while (RFC_Details.rfc_downloaded(peer.rfc_num, path)):
            peer = peer.next
            if peer == None :
                return None
        return peer

class Request_builder:

    @classmethod
    def registration(cls, port_num):
        request_string = 'GET Register P2P-DI/1.0\r\n' + 'ServerPort: ' + str(port_num) + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return request_string

    @classmethod
    def pQuery(cls, cookie_id):
        request_string = 'GET PQuery P2P-DI/1.0\r\n' + 'Cookie_id: ' + cookie_id + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return request_string

    @classmethod
    def leave(cls, cookie_id):
        request_string = 'GET Leave P2P-DI/1.0\r\n' + 'Cookie_id: ' + cookie_id + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return request_string

    @classmethod
    def keepAlive(cls, cookie_id):
        request_string = 'GET KeepAlive P2P-DI/1.0\r\n' + 'Cookie_id: ' + cookie_id + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return request_string

    @classmethod
    def re_registration(cls, host_name, cookie_id):
        request_string = 'GET Register P2P-DI/1.0\r\n' + 'Cookie_id: ' + cookie_id + '\r\n' + 'Host: ' + host_name + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return request_string

    @classmethod
    def rfcQuery(cls, cookie_id):
        request_string = 'GET RFCQuery P2P-DI/1.0\r\n' + 'Cookie_id: ' + cookie_id + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return request_string

    @classmethod
    def getRfcFile(cls, cookie_id, rfc_num):
        request_string = 'GET GetRFC P2P-DI/1.0\r\n' + 'Cookie_id: ' + cookie_id + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n' + 'RFC Num:' + str(rfc_num)
        return request_string

class Request_parser:

    @classmethod
    def parse(cls, request_string):
        request_string = request_string.splitlines()
        request_header = request_string[0].split()
        request_method = request_header[1]
        return request_method

    @classmethod
    def get_cookie_id(cls, request_string):
        request_string = request_string.splitlines()
        header_line = request_string[1]
        if 'Cookie_id' in header_line :
            cookie_id = header_line.split()
            return cookie_id[1]
        return

    @classmethod
    def get_port_num(cls, request_string):
        request_string = request_string.splitlines()
        header_line = request_string[1]
        if 'ServerPort:' in header_line :
            port = header_line.split()
            return port[1]
        return

    @classmethod
    def get_rfc_num(cls, request_string):
        request_string = request_string.split('RFC Num:')
        if len(request_string) == 2 :
            rfc_num = request_string[1]
            return rfc_num
        return

class Response_builder:

    @classmethod
    def registration(cls, status, cookie_id):
        if(status == '200'):
            phrase = 'OK'
        else:
            phrase = 'ERROR'
        response_string = 'P2P-DI/1.0 ' + status + ' ' + phrase + '\r\n' + 'cookie_id: ' + cookie_id + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return response_string

    @classmethod
    def pQuery(cls, status, data):
        if(status == '200'):
            phrase = 'OK'
        else:
            phrase = 'ERROR'
        response_string = 'P2P-DI/1.0 ' + status + ' ' + phrase + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n' + 'Peer Details:\r\n' + data
        return response_string

    @classmethod
    def leave(cls, status):
        if(status == '200'):
            phrase = 'OK'
        else:
            phrase = 'ERROR'
        response_string = 'P2P-DI/1.0 ' + status + ' ' + phrase + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return response_string

    @classmethod
    def keepAlive(cls, status):
        if(status == '200'):
            phrase = 'OK'
        else:
            phrase = 'ERROR'
        response_string = 'P2P-DI/1.0 ' + status + ' ' + phrase + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return response_string

    @classmethod
    def re_registration(cls, status):
        if(status == '200'):
            phrase = 'OK'
        else:
            phrase = 'ERROR'
        response_string = 'P2P-DI/1.0 ' + status + ' ' + phrase + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return response_string

    @classmethod
    def rfcQuery(cls, status, rfc_data):
        if(status == '200'):
            phrase = 'OK'
        else:
            phrase = 'ERROR'
        response_string = 'P2P-DI/1.0 ' + status + ' ' + phrase + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n' + 'RFC Details:\r\n' + rfc_data
        return response_string

    @classmethod
    def getRfcFile(cls, status):
        if(status == '200'):
            phrase = 'OK'
        else:
            phrase = 'ERROR'
        response_string = 'P2P-DI/1.0 ' + status + ' ' + phrase + '\r\n' + 'Time: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\r\n' + '\r\n'
        return response_string

class Response_parser:

    @classmethod
    def registration_parse(cls, response_string):
        response_string = response_string.splitlines()
        header_line = response_string[1].split()
        cookie_id = header_line[1]
        return cookie_id

    @classmethod
    def pQuery_parse(cls, response_string):
        response_string = response_string.split('Peer Details:\r\n')
        data = response_string[1]
        return data

    @classmethod
    def leave_parse(cls, response_string):
        response_string = response_string.splitlines()
        header_line = response_string[0].split()
        return header_line[2]

    @classmethod
    def keepAlive_parse(cls, response_string):
        response_string = response_string.splitlines()
        header_line = response_string[0].split()
        return header_line[2]

    @classmethod
    def re_registration_parser(cls, response_string):
        response_string = response_string.splitlines()
        header_line = response_string[0].split()
        return header_line[2]

    @classmethod
    def rfcQuery_parse(cls, response_string):
        response_string = response_string.split('RFC Details:\r\n')
        data = response_string[1]
        return data

    @classmethod
    def getRfcFile_parse(cls, response_string):
        response_string = response_string.splitlines()
        header_line = response_string[0].split()
        return header_line[2]

#=============================Testing Space========================================================================================================================
