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
            querydata = (dados["number"])
            self.cursor.execute(query, querydata)
            message = {}
            message["source"] = "users"
            if self.cursor.rowcount == 0:
                CreateUser = "INSERT INTO users (number,password) VALUES (%s,%s)"
                querydata = (dados["number"], dados["password"])
                cursor.execute(CreateUser, querydata)
                cnx.commit()
                message["result"] = "access"
            else:
                message["result"] = "denied"
            message["operation"] = "create"
            message = to_bits(message)
            self.client.send(message)
        elif self.data["operation"] == "logIn":
            dados = self.data["data"]
            querydata = (dados["number"], dados["password"])
            query = "SELECT * FROM users WHERE number=%s and password=%s"
            self.cursor.execute(query, querydata)
            message = {}
            message["source"] = "users"
            message["operation"] = "login"
            if self.cursor.rowcount > 0:
                message["result"] = "access"
            else:
                message["result"] = "denied"
            message = to_bits(message)
            self.client.send(message)
        else:
            dados = self.data["data"]
            querydata = (dados["number"], dados["password"],dados["userid"])
            query = "UPDATE users SET number=%s password=%s WHERE id=%s"
            self.cursor.execute(query, querydata)
            message = {}
            message["source"] = "users"
            message["operation"] = "login"
            if self.cursor.rowcount > 0:
                message["result"] = "access"
            else:
                message["result"] = "denied"
            message = to_bits(message)
            self.client.send(message)


def to_bits(data):
    data = json.dumps(data)
    return data.encode('utf-8')


def to_json(data):
    data = data.decode('utf-8')
    return json.loads(data)


if __name__ == "__main__":
    max_size = 1000
    try:
        cnx = mysql.connector.connect(user='root', password='',host='127.0.0.1',database='users')
    except mysql.connector.Error as err:
        if err.errno == err.code.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == err.code.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = cnx.cursor()
    address = ('localhost', 8005)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)
    server.listen(5)
    client, addr = server.accept()
    while True:
        data = client.recv(max_size)
        receive = Receiver(data, cursor, client)
        receive.start()
