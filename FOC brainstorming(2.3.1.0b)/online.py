import socket, json, re, threading

from variable import *

class Data():
    def __init__(self, userName: str,score: int, player1:list, player2:list, p1clock: int, p2clock: int, player1Hand: list, player2Hand: list, player1Decklen: int, player2Decklen: int,
        player1Trashlen: int, player2Trashlen: int, player1atk: int, player2atk: int, player1Token: int, player2Token: int, player1Luck: int, player2Luck: int, player1Tomtem: int, player2Tomtem: int):
        self.userName = userName
        self.score = score
        self.player1 = player1
        self.player2 = player2
        self.p1clock = p1clock
        self.p2clock = p2clock
        self.player1Hand = player1Hand
        self.player2Hand = player2Hand
        self.player1Decklen = player1Decklen
        self.player2Decklen = player2Decklen
        self.player1Trashlen = player1Trashlen
        self.player2Trashlen = player2Trashlen
        self.player1atk = player1atk
        self.player2atk = player2atk
        self.player1Token = player1Token
        self.player2Token = player2Token
        self.player1Luck = player1Luck
        self.player2Luck = player2Luck
        self.player1Tomtem = player1Tomtem
        self.player2Tomtem = player2Tomtem
        return True
        

class Online():
    def __init__(self):
        self.name = socket.gethostname()
        self.ip = socket.gethostbyname(self.name)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.other_server_address = []
        self.port = 10101
        self.data = 0
        print(f"Self IP:{self.ip}, Self Port:{self.port}")
        self.type = input("server(s) or client(c)")
        self.find_player()
        
    def find_player(self):
        self.other_server_address = input("input others ip(ipv4)")
        client_socket, client_address = self.start_server()
        if self.type == "c":
            self.receive_thread = threading.Thread(target=self.receve_message_main_server, args=(client_socket,client_address))
            self.receive_thread.start()
        elif self.type == "s":
            self.receive_thread = threading.Thread(target=self.receive_message_client_server, args=(client_socket,client_address))
            self.receive_thread.start()        
    

    def update(self, *data):
        if self.type == "s":
            encodeData = self.pack_data(data)
            self.send_message(encodeData)
        if self.type == "c":
            encodeData = self.pack_data_client_server(data)
            self.send_message(encodeData)
        
    def receive_message_client_server(self, client_socket, client_address, type):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                dataRes = re.findall("J->:.+?:<-J", data)
                for data in dataRes:
                    try:
                        jsonData = json.loads(data[4:-4:].replace("'", "\""))
                        self.data = Data(jsonData["userName"] ,jsonData["score"], jsonData["player1"], jsonData["player2"], jsonData["p1Clock"], jsonData["p2Clock"], jsonData["player1Hand"], jsonData["player2Hand"], 
                                         jsonData["player1Decklen"], jsonData["player2Decklen"], jsonData["player1Trashlen"], jsonData["player2Trashlen"], jsonData["player1atk"], jsonData["player2atk"],
                                         jsonData["player1Token"], jsonData["player2Token"], jsonData["player1Luck"], jsonData["player2Luck"], jsonData["player1Tomtem"], jsonData["player2Tomtem"])
                    except:
                        print("Error decoding", data)
        except Exception as e:
            print(f"{e}")
            pass
        
        
        
    def shut_down(self):
        try:
            self.client_socket.close()
            print("client_socket closed")
        except:
            pass
        try:
            self.server_socket.close()
            print("server_socket closed")
        except:
            pass
        return False
        
    def pack_data(self, data):
        score, P1Clock, P2Clock = data
        data = {"userName": self.name,
                "score":score,"player1":[], "player2":[], "p1Clock":P1Clock, "p2Clock":P2Clock,
                "player1Hand":player1Hand, "player2Hand":player2Hand,
                "player1Decklen":len(player1Deck), "player2Decklen":len(player2Deck),
                "player1Trashlen":len(player1Trash), "player2Trashlen":len(player2Trash),
                "player1atk":P1atk, "player2atk":P2atk,
                "player1Token":P1Token, "player2Token":P2Token,
                "player1Luck":P1Luck, "player2Luck":P2Luck,
                "player1Tomtem":[P1totemHP, P1totemAD], "player2Tomtem":[P2totemHP, P2totemAD]
            }
        for i in player1:
            temp = [i.health, i.attack, i.armor, i.moving, i.canATK, i.owner, i.type, i.color,i.BoardX, i.BoardY, i.anger]
            data["player1"].append(temp)
        for i in player2:
            temp = [i.health, i.attack, i.armor, i.moving, i.canATk, i.owner, i.type, i.color,i.BoardX, i.BoardY, i.anger]
            data["player2"].append(temp)
        return f"J->:{data}:<-J".encode('utf-8')
    
    
    def pack_data_client_server(self, data):
        mouseX, mouseY, types = data
        data = {"userName": self.name,
                "type": types,
                "mouseX": mouseX,
                "mouseY": mouseY
            }
        return f"J->:{data}:<-J".encode('utf-8')
    
    def send_message(self, message):
        try:
            if message:
                self.client_socket.sendall(message)
                return True
            return False
        except Exception as e:
            print(f"{e}")
            return False

    def receve_message_main_server(self, client_socket, client_address):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                dataRes = re.findall("J->:.+?:<-J", data)
                for data in dataRes:
                    try:
                        jsonData = json.loads(data[4:-4:].replace("'", "\""))
                        self.data = Data(jsonData["userName"] ,jsonData["score"], jsonData["player1"], jsonData["player2"], jsonData["p1Clock"], jsonData["p2Clock"], jsonData["player1Hand"], jsonData["player2Hand"], 
                                         jsonData["player1Decklen"], jsonData["player2Decklen"], jsonData["player1Trashlen"], jsonData["player2Trashlen"], jsonData["player1atk"], jsonData["player2atk"],
                                         jsonData["player1Token"], jsonData["player2Token"], jsonData["player1Luck"], jsonData["player2Luck"], jsonData["player1Tomtem"], jsonData["player2Tomtem"])
                    except:
                        print("Error decoding", data)
        except Exception as e:
            print(f"{e}")
            pass

    
    def start_server(self):
        try:
            self.server_socket.bind((self.ip, self.port))
        except OSError:
            print("OSError")
            return False
        self.server_socket.listen(1)
        print('Server is listening for connections...')
        
        try:
            self.client_socket.connect((self.other_server_address, self.port))
        except ConnectionRefusedError:
            print("ConnectionRefusedError")
            return False
        except socket.gaierror:
            print("socket.gaierror")
            return False
        print("Connected to server")
        client_socket, client_address = self.server_socket.accept()
        print(f'Connection from {client_address}')
        return client_socket, client_address

# Me = Online(