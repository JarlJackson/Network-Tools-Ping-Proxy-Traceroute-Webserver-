#!/usr/bin/python
# -*- coding: UTF-8 -*-

from socket import *
import thread


def handleRequest(connectionSocket, address):
    # 1. Receive request message from the client on connection socket
    mainData = connectionSocket.recv(4096)
    # 2. Extract the path of the requested object from the message (second part of the HTTP header)
    try:
        webURL = mainData.split(' ')[1]

        startURL = webURL.find("://")

        #Gets length of actual URL

        if startURL == -1:
            genURL = webURL
        else:
            genURL = webURL[(startURL + 3):]

        endURL = genURL.find("/")

        if endURL == -1:
            endURL = len(genURL)

        #Port Location

        portLocation = genURL.find(":")

        if portLocation == -1 or endURL < portLocation:
            serverport = 80
            fullURL = genURL[:endURL]
        else:
            #Adding the true port if one
            serverport = int((genURL[(portLocation + 1):])[:endURL - portLocation - 1])
            fullURL = genURL[:portLocation]

        print "Connecting to {} on port {} from address {}".format(fullURL, serverport, address)

        clientSocket = socket(AF_INET, SOCK_STREAM)

        clientSocket.connect((fullURL, serverport))
        clientSocket.send(mainData)

        #Looping data between client and server sockets
        while True:
            clientData = clientSocket.recv(4096)

            if len(clientData) > 0:
                connectionSocket.send(clientData)
            else:
                break
    except error:
        connectionSocket.close()
        print "Connection Closed"
    except IndexError:
        connectionSocket.close()
        print "Connection Closed"
    except UnboundLocalError:
        connectionSocket.close()
        print "Connection Closed"

    pass  # Remove/replace when function is complete


def startServer(serverAddress, serverPort):
    # 1. Create server socket
    mainServerSocket = socket(AF_INET, SOCK_STREAM)
    # 2. Bind the server socket to server address and server port
    mainServerSocket.bind((serverAddress, serverPort))
    # 3. Continuously listen for connections to server socket
    mainServerSocket.listen(50)
    print "Server Ready"
    # 4. When a connection is accepted, call handleRequest function, passing new connection socket
    while True:
        connection, address = mainServerSocket.accept()
        print "Connection Made"
        thread.start_new_thread(handleRequest, (connection, address))

    pass  # Remove/replace when function is complete


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
