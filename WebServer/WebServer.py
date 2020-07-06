#!/usr/bin/python
# -*- coding: UTF-8 -*-

from socket import *
import thread


def handleRequest(connectionSocket, address):
    try:
        # 1. Receive request message from the client on connection socket
        mainData = connectionSocket.recv(1024)
        # 2. Extract the path of the requested object from the message (second part of the HTTP header)
        try:
            filename = mainData.split(' ')[1]
            print "File name requested:", filename, address
            #  3. Read the corresponding file from disk
            mainFile = open(filename[1:])
            # 4. Store in temporary buffer
            outputfile = mainFile.read()
            # 5. Send the correct HTTP response error
            connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n")
            # 6. Send the content of the file to the socket
            connectionSocket.send(outputfile)
            # 7. Close the connection socket
        except UnboundLocalError:
            connectionSocket.close()
            print "Connection Closed"
        except IndexError:
            connectionSocket.close()
            print "Connection Closed"
        connectionSocket.close()
    except IOError:
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n")
        connectionSocket.send("<html><body><h1>Not Found (404)</h1></body></html>\r\n")
        connectionSocket.close()
        #pass  # Remove/replace when function is complete


def startServer(serverAddress, serverPort):
    # 1. Create server socket
    mainServerSocket = socket(AF_INET, SOCK_STREAM)
    # 2. Bind the server socket to server address and server port
    mainServerSocket.bind((serverAddress, serverPort))
    # 3. Continuously listen for connections to server socket
    mainServerSocket.listen(5)
    print "Server Ready"
    # 4. When a connection is accepted, call handleRequest function, passing new connection socket
    connection, address = mainServerSocket.accept()
    print "Connected by ip: ", address
    thread.start_new_thread(handleRequest, (connection,address))
    #  5. Close server socket
    mainServerSocket.close()
    #pass  # Remove/replace when function is complete


def customEntry():
	#User Input
    try:
        port = input("Enter Custom Port (Between 1024 and 9999): ")
    except SyntaxError:
        print "(No Custom) Default Port Running '8000'"
        port = 8000
    while True:
        if port >= 1024 & port < 10000:
            startServer("", port)
        else:
            print "Invalid Port"
            try:
                port = input("Enter Custom Port (Between 1024 and 9999): ")
            except SyntaxError:
                port = 0


customEntry()
