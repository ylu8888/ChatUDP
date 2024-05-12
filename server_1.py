'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util


class Server:
    '''
    This is the main Server Class. You will  write Server code inside this class.
    '''
    def __init__(self, dest, port, window):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))

        self.client_dict = {} #map clients to addrs

    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it.

        '''

        #print("Server is now listening on port: ", self.server_port)

        while True:
            try:
                data, addr = self.sock.recvfrom(1024) #get the msg from the client
                self.handle_client(data, addr) #process whatever client wants
            except:
                print("Error")

        #raise NotImplementedError # remove it once u start your implementation

    def handle_client(self, data, addr):
        try:
            msg_type, segno, dec_data, checksum = util.parse_packet(data.decode())
            data_split = dec_data.split()

            command = data_split[0].lower() #first input split 

            if(command == "join"):
                #print("we are join")
                #print(data_split)
                #print(data_split[2])
                
                self.join(data_split, addr)

            elif(command == "disconnect"):
                #print("we are disconnect")
               # print(data_split)
            
                self.disc(data_split, addr)

            elif(command == "request_users_list"):
                #print("we are req user list")
                #print(data_split)
                self.send_list(addr)

            elif(command == "send_message"):
                print("we are sendmsg")
                print(data_split)
                self.send_msg(data_split, addr)

            else:
                err_msg = util.make_message("err_unknown_message", 1)
                err_pkt = util.make_packet("data", 0, err_msg)
                self.sock.sendto(err_pkt.encode(), addr)

                print("disconnected: server received an unknown command")

        except:
            print("Error")
    
    def join(self, data_split, addr): #for new client trying ti join
        user = data_split[2] #this is the username

        if(len(self.client_dict) >= util.MAX_NUM_CLIENTS):  #if the server is full, reached max # of clients
            err_msg = util.make_message("err_server_full", 2)
            err_pkt = util.make_packet("data", 0, err_msg)
            self.sock.sendto(err_pkt.encode(), addr)

        elif(user in self.client_dict): #if the user is already in our client dict throw error
            err_msg = util.make_message("err_username_unavailable", 2)
            err_pkt = util.make_packet("data", 0, err_msg)
            self.sock.sendto(err_pkt.encode(), addr)

            print("disconnected: username not available")

        else: #other wise just add him to the dict
            self.client_dict[user] = addr #mapping clients to addr
            print("join:", user) 

    def disc(self, data_split, addr): #for disconnecting 
        user = data_split[2]    #this is the user
        del self.client_dict[user] #remove the client user from the dict
        print("disconnected:", user)
    
    def send_list(self, addr):
        keys = self.client_dict.keys()  #gets all the usernames
        users_list = " ".join(keys) #adds space between

        for user,myAddr in self.client_dict.items():    #loop thru the tuples in the client dict
            if addr == myAddr:  #if the addresses match
                print('request_users_list:', user)  #then print the user who requested the LIST
                break

        list_msg = util.make_message("response_users_list", 3, users_list)   #return msg to the client
        list_pkt = util.make_packet("data", 0, list_msg)
        self.sock.sendto(list_pkt.encode(), addr)

    def send_msg(self, data_split, addr):
        print("still working")


# Do not change below part of code

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"
    WINDOW = 3

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW = a

    SERVER = Server(DEST, PORT,WINDOW)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
