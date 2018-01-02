from datetime import datetime
from threading import Thread
import socket
import json
import mysql.connector


class Receiver(Thread):
    def __init__(self, data, cursor, client):
        Thread.__init__(self)
        self.data = to_json(data)
        self.cursor = cursor
        self.client = client

    def run(self):
        if self.data["operation"] == "registerEmployee" or self.data["operation"] == "registerStudent" or self.data["operation"] == "registerTeacher":
            dados = self.data["data"]
            query = "SELECT * FROM users WHERE number=%s"
            querydata = (dados["number"],)
            self.cursor.execute(query, querydata)
            print("[UsersManager] Register - Select Users to see if exist")
            message = {}
            message["source"] = "users"
            if self.cursor.rowcount <= 0:
                createuser = "INSERT INTO users (number,password,lastUpdate) VALUES (%s,%s,%s)"
                querydata = (dados["number"], dados["password"], datetime.now())
                self.cursor.execute(createuser, querydata)
                print("[UsersManager] Register - Add User")
                cnx.commit()
                message["userid"] = self.cursor.lastrowid
                message["result"] = "success"
            else:
                message["result"] = "denied"
            message["operation"] = "create"
            message = to_bits(message)
            self.client.send(message)
            print('[UsersManager] Message sent to server at', datetime.now())
        elif self.data["operation"] == "logIn":
            dados = self.data["data"]
            querydata = (dados["number"], dados["password"])
            query = "SELECT id FROM users WHERE number=%s and password=%s"
            self.cursor.execute(query, querydata)
            print("[UsersManager] LogIn - Select Users to see if exist")
            message = {}
            message["source"] = "users"
            message["operation"] = "login"
            if self.cursor.rowcount > 0:
                message["result"] = "success"
            else:
                message["result"] = "denied"
            for n in self.cursor:
                message["userid"] = n["id"]
            message = to_bits(message)
            self.client.send(message)
            print('[UsersManager] Message sent to server at', datetime.now())
        else:
            dados = self.data["data"]
            querydata = (dados["password"], dados["id"])
            query = "UPDATE users SET password=%s WHERE id=%s"
            self.cursor.execute(query, querydata)
            cnx.commit()
            print("[UsersManager] Settings - Update User")
            message = {}
            message["source"] = "users"
            message["operation"] = "login"
            message["result"] = "success"
            message = to_bits(message)
            self.client.send(message)
            print('[UsersManager] Message sent to server at', datetime.now())


def to_bits(data):
    data = json.dumps(data)
    return data.encode('utf-8')


def to_json(data):
    data = data.decode('utf-8')
    return json.loads(data)


if __name__ == "__main__":
    max_size = 1000
    cnx = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='users')
    cursor = cnx.cursor(buffered=True, dictionary=True)
    address = ('localhost', 8005)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)
    server.listen(5)
    print("[UsersManager] The server is accepting connections")
    client, addr = server.accept()
    print("[UsersManager] The server has connection")
    while True:
        data = client.recv(max_size)
        print('[UsersManager] Message receive from server at', datetime.now())
        receive = Receiver(data, cursor, client)
        receive.start()
