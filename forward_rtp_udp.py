import socket
import threading
import time
import argparse

BUFER_SIZE = 4 * 1024 

def forward(ip, port_in, port_forward):
    socket_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_in.bind((ip, port_in))
    socket_in.settimeout(60.0)
    print ("*** Listening in %s:%s" % ( ip, port_in ))

    socket_forward = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_forward.bind((ip, port_forward)) # Bind to the port data came in on
    data_f, addr_f = socket_forward.recvfrom(BUFER_SIZE)

    print ("*** Listening forward %s:%s" % ( ip, port_forward ))
    print ("*** Start forwarding, local %s:%d" % ( addr_f[0], addr_f[1] ))

    while True:
        data, addr = socket_in.recvfrom(BUFER_SIZE)
        # print (len(data))
        # print (data)
        socket_forward.sendto(data, (addr_f[0], addr_f[1] ))


parser = argparse.ArgumentParser(description="Forward UDP port")
parser.add_argument("-a", dest="ip", required=True)
parser.add_argument("-p", dest="port_in", default=64154, type=int)
parser.add_argument("-o", dest="port_forward", default=64155, type=int)
args = parser.parse_args()
print(args)


while True:
    try:
        forward(args.ip, args.port_in, args.port_forward)
    except Exception as e:
        print(e)
        pass
