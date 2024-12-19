import socket, json, re
import threading, time
from pwn import log
        

class Client:
    def __init__(self, server_address: str, name: str) -> None:
        self.name = name
        self.server_close = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (server_address, 40000)
        # self.datas: dict[str, ] = {}
        self.cards: list[str] = []
        log.success("Client initialized")
        
        while not self.connect(): log.success("Retrying to connect...")
        

    def connect(self) -> bool:
        time.sleep(1)
        log.success("Trying to connect to server...")
        try:
            time.sleep(1.5)
            self.client_socket.connect(self.server_address)
            self.receive_thread = threading.Thread(target=self.receive_data, args=[self.client_socket])
            self.receive_thread.start()
            log.success("Connected")
            return True
        except KeyboardInterrupt:
            print()
            log.success("Stop the process")
            return True
        except Exception as e:
            print(e)
            time.sleep(3)
        except:
            log.error("Server has not activated, please wait...")
            # self.server_close = True
            return False
        return False
        
    def receive_data(self, client_socket: socket.socket) -> None:
        # try:
            while True:
                data: str = str(client_socket.recv(2048).decode('utf-8'))
                if not data:
                    break
                dataRes = re.findall("J->:.+?:<-J", data)
                print(dataRes)
                if dataRes:
                    for data in dataRes:
                        # try:
                            jsonData = json.loads(data[4:-4:].replace("'", "\""))
                            print(jsonData)
                            print("Received JSON data:", jsonData)
                        # except Exception as e:
                        #     print("Error decoding", data, e)

        # except Exception as e:
        #     print(e)
        #     if str(e) != "[WinError 10053] 連線已被您主機上的軟體中止。":
        #         log.success("Server isn't started, relunch the server to connet to it.")
            

        #    client_socket.close()
        
    def send_data(self, action: str | None=None) -> bool:
        try:
            if action != None:
                data = {"players" : self.name, "action" : action}
                print("sent:", data)
                self.client_socket.send(f"J->:{data}:<-J".translate(str.maketrans("()", "[]")).encode('utf-8'))
                log.success("sent:", data)
            else:
                return False
            return True
        except Exception as e:
            print(e)
            log.success("Server are closed.")
            return False

    
    
def main() -> int:
    robin = Client("25.42.132.180", "robin")



    return 0    
        
if __name__ == "__main__":
    main()