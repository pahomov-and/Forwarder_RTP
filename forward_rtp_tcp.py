import socket
import threading
import time
import argparse

BUFER_SIZE = 4 * 1024 

# def main():
#     thread.start_new_thread(server, () )
#     lock = thread.allocate_lock()
#     lock.acquire()
#     lock.acquire()

def forward(ip, port_in, port_forward):

    socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_in.bind((ip, port_in))
    socket_in.listen(1)
    print ("*** listening on %s:%i" % ( ip, port_in ))

    socket_forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_forward.bind((ip, port_forward))
    socket_forward.listen(1)
    print ("*** listening on %s:%i" % ( ip, port_forward ))


    client_in_socket, client_in_address = socket_in.accept()
    print ("*** accept on %s:%i" % ( client_in_address, port_in ))


    client_forward_socket, client_forward_address = socket_forward.accept()
    print ("*** accept on %s:%i" % ( client_forward_address, port_forward ))

    while True:
        data, addr = client_in_socket.recvfrom(BUFER_SIZE)
        print (len(data))
        # print (data)
        client_forward_socket.sendall(data)



# def forward(source, destination, description):
#     data = ' '
#     while data:
#         data = source.recv(BUFER_SIZE)
#         print "*** %s: %s" % ( description, data )
#         if data:
#             destination.sendall(data)
#         else:
#             source.shutdown(socket.SHUT_RD)
#             destination.shutdown(socket.SHUT_WR)

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



# if __name__ == '__main__':
#     main()