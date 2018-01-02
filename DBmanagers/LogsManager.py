import socket
import threading
from datetime import datetime
import mysql.connector

conn = mysql.connector.connect(host="localhost",user='root', database='logs')
cursor = conn.cursor()


def insertLog(description):
    add_log = ("INSERT INTO logs "
                      "(description)"
                      "VALUES (%s)")
    print('log: '+description+' was inserted in logs db')
    cursor.execute(add_log, (description,))
    conn.commit()


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        print('Starting server at', datetime.now())
        print('Waiting for a client to call.')


    def listen(self):
        self.server.listen(5)
        while True:
            client, address = self.server.accept()
            print('Client called')
            #client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        max_size = 1024
        while True:
            try:
                data = client.recv(max_size)
                if data:
                    data=data.decode('utf-8')
                    print(data)
                    insertLog(data)
                    #response = b'data received'
                    #client.send(response)

            except:
                client.close()
                print('socket closed')
                return False



if __name__ == "__main__":
    while True:
        ThreadedServer('localhost',8003).listen()