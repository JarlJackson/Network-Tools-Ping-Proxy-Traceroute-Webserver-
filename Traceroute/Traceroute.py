#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii

maxjumps = 30
beginTime = time.time()

ICMP_ECHO_REQUEST = 8  # ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0  # ICMP type code for echo reply messages


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = ord(string[count + 1]) * 256 + ord(string[count])
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    if sys.platform == 'darwin':
        answer = socket.htons(answer) & 0xffff
    else:
        answer = socket.htons(answer)

    return answer


def createpacket():
	#Creating the packet + Data
    mainID = os.getpid() & 0xFFFF

    mainheader = struct.pack('BBHHH', ICMP_ECHO_REQUEST, 0, 0, mainID, 1)

    mainData = b'Jarl'

    correctchecksum = checksum(mainheader + mainData)

    mainheader = struct.pack('BBHHH', ICMP_ECHO_REQUEST, 0, correctchecksum, mainID, 1)

    packet = mainheader + mainData

    return packet


def pingroute(host, attempts, timeout, port, packetloss=0):
	#Looping for TTL & Max tries (Allows to loop each node)
    for TTL in range(1, maxjumps):
        for maxtries in range(attempts):
            destinationAddress = socket.gethostbyname(host)
			
			#Attempting to allow UDP and ICMP
            if port == 0:
                mainsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            elif port == 1:
                mainsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            else:
                mainsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

            mainsocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', TTL))

            mainsocket.settimeout(timeout)

            corepacket = createpacket()
			
			#Sending the data
            mainsocket.sendto(corepacket, (destinationAddress, 0))

            timepacketsent = time.time()
			
			#Wiaitng on reply 
            waiting = select.select([mainsocket], [], [], timeout)

            if waiting[0] == []:
                packetloss += 1
                print ("*		*		*		Timed Out")
            else:
				#Extracting Data
                timepacketRecieved = time.time()
                recoveredPacketBytes, address = mainsocket.recvfrom(1024)
                ICMPHeaderData = recoveredPacketBytes[20:28]
                type, packetcode, packetchecksum, packetID, packetSequence = struct.unpack("BBHHH", ICMPHeaderData)

				#Hit a Node
                if type == 11:
                    try:
                        hostname = socket.gethostbyaddr(address[0])
                    except socket.herror:
                        hostname = "*"
						#Calcualting variables
                    print "{} Reply from {} - {} in {} millseconds".format(TTL, address[0], hostname[0], round(
                        (timepacketRecieved - timepacketsent) * 1000, 2))
				#Hit the end
                elif type == 0:
                    try:
                        hostname = socket.gethostbyaddr(address[0])
                    except socket.herror:
                        hostname = "*"
						#Calcualting variables
                    print "{} Reply from {} - {} in {} millseconds".format(TTL, address[0], hostname[0], round(
                        (timepacketRecieved - timepacketsent) * 1000, 2))
                    print "Packet Loss: {} %".format(round((float(packetloss) / TTL) * 100), 2)
                    return


def customInput():
	#User Input
    name = raw_input("Enter Server Address (Host OR IP): ")

    while True:

        if name != "":
            host = name
            break
        else:
            print "No Server Address Given"
            name = raw_input("Enter Server Address (Host OR IP): ")
    try:
        attempts = input("Enter how many tries per node?: ")
    except SyntaxError:
        print "(No Custom) - Default Selected '3'"
        attempts = 3

    while True:

        if attempts > 0:
            attempts = attempts
            break
        else:
            print "No Attempts Given"
            attempts = input("Enter how many tries per node?: ")

    try:
        timeout = input("Enter Timeout: ")
    except SyntaxError:
        print "(No Custom) - Default Selected '1 Second'"
        timeout = 1

    while True:

        if timeout != 0:
            timeout = timeout
            break
        else:
            print "Invalid Timeout"
            timeout = input("Enter Timeout: ")


    try:
        port = raw_input("Enter ICMP OR UDP: ")
    except SyntaxError:
        print "(No Custom) - Default Selected ICMP'"
        port = 0

    while True:

        if port == "ICMP":
            port = 0
            break
        elif port == "UDP":
            port = 1
            break
        else:
            print "Invalid Port"
            port = raw_input("Enter ICMP OR UDP: ")

    pingroute(host, attempts, timeout, port)


customInput()
