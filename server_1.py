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
            data, addr = self.sock.recvfrom(1024) #get the msg from the client
            self.handle_client(data, addr) #process whatever client wants
            

    def handle_client(self, data, addr):
        
        msg_type, seqno, dec_data, checksum = util.parse_packet(data.decode())
        data_split = dec_data.split()

        command = data_split[0].lower() #first input argument is the command

        if(command == "join"):  
            self.join(data_split, addr)

        elif(command == "disconnect"):
            self.disc(data_split, addr)

        elif(command == "request_users_list"):
            self.send_list(addr)

        elif(command == "send_message"):
            self.send_msg(dec_data, data_split, addr)

        else:   #if the command is invalid
            err_msg = util.make_message("err_unknown_message", 2)
            err_pkt = util.make_packet("data", 0, err_msg)
            self.sock.sendto(err_pkt.encode(), addr)

            user = data_split[2] #this is the username
            print(f"disconnected: {user} sent unknown command")

        
    
    def join(self, data_split, addr): #for new client trying ti join
        user = data_split[2] #this is the username

        if(len(self.client_dict) >= util.MAX_NUM_CLIENTS):  #if the server is full, reached max # of clients
            err_msg = util.make_message("err_server_full", 2)
            err_pkt = util.make_packet("data", 0, err_msg)
            self.sock.sendto(err_pkt.encode(), addr)

            print("disconnected: server full")

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
    
    def send_list(self, addr): #sending the list of users
        keys = self.client_dict.keys()  #gets all the usernames
        users_list = " ".join(keys) #adds space between the users in list

        for user,myAddr in self.client_dict.items():    #loop thru the tuples in the client dict
            if addr == myAddr:  #if the addresses match
                print('request_users_list:',user)  #then print the user who requested the LIST
                break

        list_msg = util.make_message("response_users_list", 3, users_list)   #return msg to the client
        list_pkt = util.make_packet("data", 0, list_msg)
        self.sock.sendto(list_pkt.encode(), addr)

    def send_msg(self, dec_data, data_split, addr):
        user = data_split[2]    #this is the user
        print("msg:", user)

        #this is dec data #send_message 63 ady ['msg', '2', 'ady', 'bib', 'hello', 'my', 'frog', 'friend']
        
        start_index = dec_data.find('[')    #extract the array out
        end_index = dec_data.find(']')

        array_str = dec_data[start_index:end_index+1]    #only care ab thte array
        msg_arr = eval(array_str)   #convert to array
        #print('le real msg_arr', msg_arr)
       
        x = 2 #this is where user starts
        user_len = msg_arr[1] #this is how many users are being sent a mesage
        #print('this is the user-len', user_len)
        for i in range(int(user_len)): #loop from i to # of users who is being sent a message
            msged_user = msg_arr[x] #this is the user who is receiving the message
            x += 1

            if(msged_user not in self.client_dict):
                print(f"msg: {user} to non-existent user {msged_user}")

            else:
                user_addr = self.client_dict[msged_user]
                actual_msg = " ".join(msg_arr[(2 + int(user_len)):])#this is the actual message being sent

                #print('this the message', actual_msg)

                return_arr = ["", ""]   #response msg will look like ["ady", "hello my friend"]
                return_arr[0] = user
                return_arr[1] = actual_msg
                
                sent_msg = util.make_message("forward_message", 4, return_arr)   #send the message to all the useres in for loop!
                sent_pkt = util.make_packet("data", 0, sent_msg)
                self.sock.sendto(sent_pkt.encode(), user_addr)


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
