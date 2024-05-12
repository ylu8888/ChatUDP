'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import util


'''
Write your code inside this class. 
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen 
for incoming messages in this function.
'''

class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port, window_size):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username

    
    #cleint is added to server when join req
    #use dict to map clients to addrs
    #when serv full it should be clients.size() >= util.max_num_clients
    #disconnect the client when he does quit, unknwon msg, serverfull, and username unavailable
    #keep seq number at 0 for all of part 1
    #when u do make packet the first parameter should be "data"
    #do the split("|") to decode the original message in the packet the server receives 


    #when u do sock.recv from the server side you can get the address

    def start(self):
        '''
        Main Loop is here
        Start by sending the server a JOIN message. 
        Use make_message() and make_util() functions from util.py to make your first join packet
        Waits for userinput and then process it
        '''

        self.send_join()

        while True:
            
            user_input = input() #receive input from user thru command line

            self.process_input(user_input) #process whatever command the user does

            # except (KeyboardInterrupt): #if user hits ctrl C or something
            
            #     sys.exit()

        #raise NotImplementedError # remove it once u start your implementation
            

    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        '''

        while True:
            
            res_data, addr = self.sock.recvfrom(1024)
            msg_type, seqno, dec_data, checksum = util.parse_packet(res_data.decode())

            data = dec_data.split() #split the server res data into array

            command = data[0].lower() #this is the msg / first input of split data

            if(command == "response_users_list"):
                users_list = data[2:]
                sorted_users = sorted(users_list) # need to sort in alphabetical order the users
                print("list:", " ".join(sorted_users))

            elif(command == "forward_message"): 
                #print('this the dec data', dec_data) # forward_message 2 ['ady', 'hello my frog friend']
                #print('this the split data', data)

                start_index = dec_data.find('[')    #extract the array out
                end_index = dec_data.find(']')

                array_str = dec_data[start_index:end_index+1]    #only care ab thte array
                msg_arr = eval(array_str)

                print(f"msg: {msg_arr[0]}: {msg_arr[1]}")
                
            
            elif(command == "err_unknown_message"): #if we get an error, print it and quit
                self.sock.close()
                print("disconnected: server received an unknown command")
               
                
                #sys.exit()

            elif(command == "err_server_full"):
                self.sock.close()
                print("disconnected: server full")
               
                #sys.exit()
                
                

            elif(command == "err_username_unavailable"):
                self.sock.close()
                print("disconnected: username not available")
               
                #sys.exit()
            
            # else: #some type of error happened
            #    
            #     sys.exit()


            # except: #some type of error happens
            #   
            #     sys.exit()
        #raise NotImplementedError # remove it once u start your implementation

    def send_join(self): #send a join message to server
        join_message = util.make_message("join", 1, self.name)
        my_packet = util.make_packet("data", 0, join_message)
        self.sock.sendto(my_packet.encode(), (self.server_addr, self.server_port))

    def process_input(self, user_input): #handle whatever commands the client wants quit, list help, msg
        input = user_input.split()   #split the input into an array for simplicity

        command = input[0].lower() # this is the first command, changed to lower case

        if(command == "quit"): 
            self.quit()
            print("quitting")
            sys.exit()

        elif(command == "list"):
            self.list()
        
        elif(command == "help"):
            self.help()
        
        elif(command == "msg"):
            self.send_msg(input)

        else:   #if the command is not any of the above
            print("incorrect userinput format")
           
            # sys.exit()

    def quit(self): #send a message to the server and tell him that a client is quitting, so remove client frm dict
        quit_message = util.make_message("disconnect", 1, self.name)
        quit_packet = util.make_packet("data", 0, quit_message) 

        self.sock.sendto(quit_packet.encode(), (self.server_addr, self.server_port))

    def list(self): #send msg to server asking to request list of all the usernames of clients, names must be in ascending order
        list_message = util.make_message("request_users_list", 2, self.name)
        list_packet = util.make_packet("data", 0, list_message) 

        self.sock.sendto(list_packet.encode(), (self.server_addr, self.server_port))
    
    def help(self): #prints all possible user inputs and the format input
        print("All the user inputs and the format input:")
        print("Message: msg <number_of_users> <username1> <username2> … <message>")
        print("Available Users: list")
        print("Help: help")
        print("Quit: quit")


    def send_msg(self, input):  #client sends msg to server
        msg_message = util.make_message("send_message", 4, f"{self.name} {input}")
        msg_packet = util.make_packet("data", 0, msg_message) 

        self.sock.sendto(msg_packet.encode(), (self.server_addr, self.server_port))


#part 2
#send a start packet, once thats ACKED, 
#then sent a data packet with join quit whatever query
#once thats acked
#send an END
#and keep doing that on repeat


# Do not change below part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    WINDOW_SIZE = 3
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW_SIZE = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT, WINDOW_SIZE)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
