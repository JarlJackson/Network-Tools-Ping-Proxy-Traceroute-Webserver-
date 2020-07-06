#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select

results = []
beginTime = time.time()
packetloss = 0

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


def receiveOnePing(mainSocket, timepacketsent, ID, timeout):
    global packetloss
    countdown = timeout

    # 1. Wait for the socket to receive a reply
    while True:

        waiting = select.select([mainSocket], [], [], countdown)

        if waiting[0] == []:
            packetloss += 1
            return

        timepacketRecieved = time.time()

        recoveredPacketBytes, address = mainSocket.recvfrom(1024)

        ICMPHeaderData = recoveredPacketBytes[20:28]

        type, packetcode, packetchecksum, packetID, packetSequence = struct.unpack(
            "BBHHH", ICMPHeaderData
        )

        if type == 3:
            print "Destination Unreachable"
            print "-----------------------"
            if packetcode == 1:
                print "Host Unreachable"
            elif packetcode == 11:
                print "Destination Network Unreachable"

        if packetID == ID:
            return timepacketRecieved - timepacketsent

    # 2. Once received, record time of receipt, otherwise, handle a timeout
    # 3. Compare the time of receipt to time of sending, producing the total network delay

    # 4. Unpack the packet header for useful information, including the ID
    # 5. Check that the ID matches between the request and reply
    # 6. Return total network delay
    pass  # Remove/replace when function is complete


def sendOnePing(mainSocket, destinationAddress, mainID):
    # 1. Build ICMP header
    mainHeader = struct.pack('BBHHH', ICMP_ECHO_REQUEST, 0, 0, mainID, 1)

    mainData = b'Jarl'

    correctCheckSum = checksum(mainHeader + mainData)

    mainHeader = struct.pack('BBHHH', ICMP_ECHO_REQUEST, 0, correctCheckSum, mainID, 1) + mainData

    # 4. Send packet using socket

    mainSocket.sendto(mainHeader, (destinationAddress, 1))

    #  5. Record time of sending


def doOnePing(destinationAddress, timeout):
    # 1. Create ICMP socket
    mainSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    mainID = os.getpid() & 0xFFFF

    # 2. Call sendOnePing function
    sendOnePing(mainSocket, destinationAddress, mainID)
    # 3. Call receiveOnePing function
    mainDelay = receiveOnePing(mainSocket, time.time(), mainID, timeout)
    # 4. Close ICMP socket
    mainSocket.close()
    # 5. Return total network delay
    return mainDelay

    pass  # Remove/replace when function is complete


def ping(host, timeout, attempts):
    totalattempts = attempts
    try:
        hostname = host
        # 1. Look up hostname, resolving it to an IP address
        host_ip = socket.gethostbyname(hostname)
        print "Hostname:", hostname
        print "IP:", host_ip
    except:
        print("Error")

    # 2. Call doOnePing function, approximately every second
    while attempts > 0:
        attempts = attempts - 1
        mainDelay = doOnePing(hostname, timeout)
        results.append(round(mainDelay * 1000, 2))
        if mainDelay == None:
            print "Timed Out - Packet Lost"
        else:
            print "Reply from {} in {} milliseconds".format(host_ip, round(mainDelay * 1000, 2))
        time.sleep(timeout)

    # 3. Print out the returned delay
    # 4. Continue this process until stopped
    average = (sum(results) / results.__len__())
    minimum = min(results)
    maximum = max(results)
    print "Min: {} ms Max: {} ms Average: {} ms Packet Loss: {} %".format(minimum, maximum, average, round(
        (packetloss / float(totalattempts)) * 100), 2)
    pass  # Remove/replace when function is complete


def customInput():
    # User Input Function
    name = raw_input("Enter Server Address (Host OR IP): ")

    while True:

        if name != "":
            host = name
            break
        else:
            print "No Server Address Given"
            # Custom IP
            name = raw_input("Enter Server Address (Host OR IP): ")
    try:
        attempts = input("Enter how many pings: ")
    except SyntaxError:
        print "(No Custom) - Default Selected '10'"
        attempts = 10

    while True:

        if attempts > 0:
            attempts = attempts
            break
        else:
            print "No Attempts Given"
            # Custom Attemtps
            attempts = input("Enter how many pings: ")

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
            # Custom Timeout
            timeout = input("Enter Timeout: ")

    ping(host, timeout, attempts)


customInput()
