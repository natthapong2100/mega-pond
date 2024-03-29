import socket
import threading
import sys
import time
import random
from queue import Queue

# sys.path.append('../src')
from FishData import FishData
from PondData import PondData
from Payload import Payload
from server import PORT

import pickle
IP = socket.gethostbyname(socket.gethostname())
ADDR = (IP, PORT)
MSG_SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"


class Client:
    def __init__(self,pond):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = IP
        self.port = PORT
        self.addr = ADDR
        self.connected = True
        self.other_ponds = {}
        self.msg = self.connect()
        self.payload = Payload()
        self.pond = pond
        self.messageQ = []

    def get_msg(self):
        while True:
            time.sleep(0.5)
            msg = pickle.loads(self.client.recv(MSG_SIZE))
            if(msg):
                self.messageQ.append(msg)
                print("Recieve", msg.action)
                self.handle_msg(msg)
            else:
                break
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            print(f"Client connected ")
            return "Connected"
        except:
            print("Can not connect to the server")

    def send_pond(self):
        try:
            while True:
                time.sleep(2)
                self.payload.action = "SEND"
                self.payload.data = self.pond
                #print("Client send :",self.pond)
                self.client.send(pickle.dumps(self.payload))
                #msg =  pickle.loads(self.client.recv(MSG_SIZE))
                #return self.handle_msg(msg)

        except socket.error as e:
            print(e)

    def migrate_fish(self, fishData , destination):
        ### Migration takes a special object for the payload to pickup : The destination pond's name 
        try:

            migration = {
                "destination" : destination,
                "fish" : fishData
            }
            self.payload.action = "MIGRATE"
            self.payload.data = migration

            self.client.send(pickle.dumps(self.payload))
            print("=======MIGRATED=======")            
            ### Handle our fish in the pond
            # // TO BE IMPLEMENTED

            msg =  pickle.loads(self.client.recv(MSG_SIZE))
            return self.handle_msg(msg)
            

            # print("Client send :",pond)
            # next_pond = random.random_choice(self.other_ponds.keys())
            # self.client.send("MIGRATE FROM sick_salmon TO "+ next_pond + " " + pickle.dumps(fishData))
            # msg =  pickle.loads(self.client.recv(MSG_SIZE))
            # return self.handle_msg(msg)
        except socket.error as e:
            print(e)
    
    def disconnect(self) :
        try:
            self.payload.action = DISCONNECT_MSG
            print("Disconnecting...")
            self.client.send(pickle.dumps(self.payload))
            return self.client.recv(MSG_SIZE)

        except socket.error as e:
            print(e)

    def handle_msg(self, msg):
        msg_action = msg.action
        msg_object = msg.data
        #print(self.messageQ)

        if(msg_action == "SEND") :
            self.other_ponds[msg_object.pondName] = msg_object #Update in the dict key = pondname, values = <PondData>
            print(self.other_ponds)
            return msg
        
        if(msg_action == "MIGRATE"):
            if(self.pond.pondName == msg_object["destination"]):
                print("=======RECIEVED MIGRATION=======")
                self.pond.addFish(msg_object["fish"])
                print(self.pond.fishes)
                print("================================")
        
        else:
            pass
        # if msg[:7] == "MIGRATE":
        #     pass
        # elif msg[:4] == "JOIN":
        #     pass
        # elif msg[:11] == "DISCONNECT":
        #     pass
        # else:
        #     print(f"Vivisystem : {msg}")
        #     return msg
if __name__ == "__main__":

    f1 = FishData("pla","123456")
    f2 = FishData("pla","321412")
    f3 = FishData("pla","123456")
    p = PondData("pla")
    p.addFish(f1)
    p.addFish(f2)
    p.addFish(f3)
    connected = True
    c = Client(p)
    msg_handler = threading.Thread(target=c.get_msg)   
    msg_handler.start() 
    send_handler = threading.Thread(target=c.send_pond)
    send_handler.start()
    c.migrate_fish(p.fishes[0],"mega-pond")
    time.sleep(5)
    c.migrate_fish(p.fishes[1],"mega-pond")
    time.sleep(5)

