import socket
import threading
import sys
from time import sleep
from random import randint

HEADER = 64
HOST = "192.168.149.1"
PORT = 5050

connections = []
waiting = []    

new_snakes = []
apples = [[randint(5, 110)*10, randint(5, 70)*10] for _ in range(10)]


def handle_client(conn, addr):
    global new_snakes, score
    
    nickname = receive(conn)
    data = receive(conn)
    threading.current_thread().nickname = nickname
    threading.current_thread().conn = conn
    
    # sending all players new player joined
    send_to_all(data, conn)
    # sending all snakes
    new_snakes = []
    for c in connections:
        if c != conn:
            send(c, "[ASK_POS]")
            sleep(0.5)
            send(conn, new_snakes[-1])
    # sending all apples
    for a in apples:
        send(c, f"[APPLE+]|{','.join(map(str,a))}")

    send_to_all(f"[CHAT]|{nickname} joined!")

    while 1:
        data = receive(conn)
        prefix = data.split("|")[0]
        if prefix == "[NEW]":
            new_snakes.append(data)
        elif prefix == "[APPLE-]":
            apples.remove(list(map(int, data.split("|")[1].split(","))))
            #[APPLE-]|x,y
            #"x,y"
            #[x,y]
            send_to_all(data, conn)
            apples.append([randint(5, 100)*10, randint(5, 70)*10])
            send_to_all(f"[APPLE+]|{','.join(map(str,apples[-1]))}")
            # converts each coordinate to a string: ["70", "50"], and ','.join(["70", "50"]) joins them with commas to produce "70,50"
        elif prefix == "[CHAT]":
            send_to_all(data)
        else:
            send_to_all(data, conn)


def handle_disconnect(args):
    errors = [ConnectionResetError,
              ConnectionAbortedError,
              ConnectionError,
              ConnectionRefusedError]
    nickname = threading.current_thread().nickname
    if args.exc_type in errors:
        print(f"Connection lost with client {nickname}. Err: {args.exc_type.__name__}")
        connections.remove(threading.current_thread().conn)  # remove client from connections list
        send_to_all(f"[CHAT]|{nickname} left")            # send to all players that client left
        send_to_all(f"[LEFT]|{nickname}")     
    else:
        # if error is not in errors list, then it's not handled by us, so we pass it to default exception hook
        sys.__excepthook__(
            args.exc_type, args.exc_value, args.exc_traceback)


def send_to_all(msg, excluded=None):
    for c in connections:
        if c != excluded:
            send(c, msg)


def receive(conn):
    msg_len = conn.recv(HEADER)
    msg_len = int(msg_len.decode())
    #msg_len has 64 bytes, so we need to decode it and then remove spaces
    msg = conn.recv(msg_len).decode()
    return msg


def send(conn, msg):
    msg_len = str(len(msg.encode()))
    #making 64 bytes long header
    msg_len = msg_len.encode() + b" "*(HEADER-len(msg_len))
    conn.send(msg_len)
    conn.send(msg.encode())

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock: # closing socket after exiting with block, good practice
        sock.bind((HOST, PORT))
        sock.setblocking(True) #When a socket is in blocking mode, operations such as recv() and accept() block until there is valid data to read or the socket is listening.
        sock.listen()
        print(f"Server is listening on {(HOST,PORT)}")
        while True:
            conn, addr = sock.accept()
            print(f"New client connected from {addr}")
            connections.append(conn)
            print(f"Active connections: {len(connections)}")
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()


if __name__ == "__main__":
    threading.excepthook = handle_disconnect 
    main()
