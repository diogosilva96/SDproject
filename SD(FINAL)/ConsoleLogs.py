import socket
from datetime import datetime
import json
from threading import Thread


class WriteMessage(Thread):
    def __int__(self, data):
        self.pm_data = data

    def run(self):
        self.pm_data = self.pm_data.decode('utf-8')
        self.pm_data = json.loads(self.pm_data)
        print(self.pm_data)


address = ('localhost', 8002)
max_size = 1000
print('Starting server at', datetime.now())
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)
server.listen(5)
client, addr = server.accept()

while True:
    pm_recv = client.recv(max_size)
    ThreadMessage = WriteMessage(pm_recv)
    ThreadMessage.start()
