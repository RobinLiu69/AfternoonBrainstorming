import socket, json, re
import threading
from pwn import log

class Items:
    def __init__(self, name: str, history: list[str]=[], covered: int=0) -> None:
        self.name: str = name
        self.history: list[str] = history
        self.covered: int = covered
        
class Datas:
    def __init__(self, name: str, items: list[Items]=[], players: list[str]=[]) -> None:
        self.name: str = name
        self.items: list[Items] = items
        self.players: list[str] = players
        
    def update(self, kwargs: dict) -> None:
        for key, value in kwargs.items():
            if key == "items":
                self.items: list[Items] = list(Items(item["name"], item["history"], int(item["covered"])) for item in value)
            elif key == "players":
                self.players = value

class Server:
    def __init__(self, cards: list[str]=[], datas: dict[Datas]={}) -> None:
        log.success("Server initialized")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ("0.0.0.0", 40000)
        # self.server_address = (socket.gethostbyname(socket.gethostname()), 40000)
        # self.server_address = ("25.61.96.35", 32768)
        log.success(f"Server address(IPv4):{self.server_address}")
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(2)
        log.success('Waiting clients to connect...')
        self.clients: list[socket.socket] = []
        self.cards: list[str] = cards
        self.datas: dict[str, Datas] = datas
        self.find_client()

    def handle_client(self, client_socket: socket.socket) -> None:
        try:
            while True:
                data: str = str(client_socket.recv(4096).decode('utf-8'))
                if not data:
                    break
                dataRes: str = re.findall("J->:.+?:<-J", data)
                cardRes: str = re.findall("C->:.+?:<-C", data)
                if dataRes or cardRes:
                    for data in dataRes:
                        try:
                            jsonData: str = json.loads(data[4:-4:].replace("'", "\""))
                            res: Datas = self.datas.get(jsonData["room_name"], None)
                            if not res:
                                self.datas[jsonData["room_name"]] = Datas(jsonData["room_name"], jsonData["items"], jsonData["players"])
                            else:
                                res.update(jsonData)
                        except:
                            print("Error decoding", data)
                    for data in cardRes:
                        try:
                            jsonData: str = json.loads(data[4:-4:].replace("'", "\""))
                            self.cards: Datas = jsonData
                        except:
                            print("Error decoding", data)
                    
                    self.broadcast()
        except:
            pass

        client_socket.close()

    def broadcast(self) -> None:
        for client in self.clients:
            try:
                for data in self.datas.items():
                    self.send_data(client, data=data[1])
            except Exception as e:
                log.success(f"Remove client from {client}")
                self.clients.remove(client)
                self.broadcast()
                
    def send_data(self, client_socket: socket.socket, data:Datas = None, cards: list[str]=None) -> None:
        if data != None:
            data = {"room_name" : data.name, "items" : [{"name": item.name, "history": item.history, "covered": int(item.covered)} for item in data.items], "players" : data.players}
            if data["room_name"] == "livingroom": print(data)
            print(client_socket.send(f"J->:{data}:<-J".encode('utf-8')))
        if cards != None:
            client_socket.send(f"C->:{cards}:<-C".encode('utf-8'))
        
    def find_client(self) -> None:
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append(client_socket)
                log.success(f"Connect from:{client_address}")
                for data in self.datas.items():
                    self.send_data(client_socket, data=data[1])
                self.send_data(client_socket, cards=self.cards)
                client_thread = threading.Thread(target=self.handle_client, args=[client_socket])
                client_thread.start()
                
        except KeyboardInterrupt:
            self.server_socket.close()
            log.success("Server shut down")
            
        # except Exception as e:
        #     print("hit", e)
            
        # finally:
        #     for client in self.clients:
        #         client.close()
        #     self.server_socket.close()



if __name__ == "__main__":
    server = Server(cards=["Take", "Take"], datas={"kitchen": Datas("kitchen", list(map(Items, ["Pork", "Mud", "Knife", "Knife", "Pork"])), ["robin"]), 
                                                   "yard": Datas("yard", list(map(Items, ["Pork", "Pork", "Knife", "Knife", "Pork"])), ["robin"]), 
                                                   "bedroom": Datas("bedroom", list(map(Items, ["Pork", "Pork", "Pork", "Knife", "Pork"])), ["robin"]), 
                                                   "study": Datas("study", list(map(Items, ["Pork", "Pork", "Pork", "Pork", "Knife"])), ["robin"]), 
                                                   "livingroom": Datas("livingroom", list(map(Items, ["Pistol", "Pistol", "Pork", "Pork", "Chandelier"])), ["robin"])})
    

  
    server.server_socket.close()