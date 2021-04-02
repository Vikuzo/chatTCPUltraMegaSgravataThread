from socket import *
# import sys


def socket_tcp_generation():
    return socket(AF_INET, SOCK_STREAM)


def server_bind(serverSocket, serverName, serverPort):
    serverSocket.bind((serverName, serverPort))
    serverSocket.listen(5)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)


def server_waiting_for_connection(serverSocket):
    clientSocket, address = serverSocket.accept()
    return clientSocket, address


def server_close(serverSocket):
    serverSocket.close()


def client_connection(clientSocket, serverName, serverPort):
    clientSocket.connect((serverName, serverPort))


def client_close(clientSocket):
    clientSocket.close()


def send(Socket, message):
    Socket.send(message.encode('utf-8'))


def receive(Socket, buffer):
    return Socket.recv(buffer).decode('utf-8')
