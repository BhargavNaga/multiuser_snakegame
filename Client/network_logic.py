import socket
import sys
import tkinter as tk
from tkinter import messagebox
from getmac import get_mac_address
import re
SIZE = 4096
FORMAT = "utf-8"


HEADER = 64


def handle_disconnect(args):
    errors = [ConnectionResetError,
              ConnectionAbortedError,
              ConnectionError,
              ConnectionRefusedError]
    if args.exc_type in errors:
        print(
            f"Connection lost with remote server. Err: {args.exc_type.__name__}")
        disconnected()
    else:
        sys.__excepthook__(
            args.exc_type, args.exc_value, args.exc_traceback)


def connect(addr: tuple) -> str:
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Connecting...")
    try:
        conn.connect(addr)
    except Exception as e:
        print("Can't connect to the remote server.")
        print("Error: ", e)
        exit()
    print(f"Connected to server at {addr}")

    return conn

# # #


def game_entry():
    global count1
    global count2 
       
    count1 = 0
    count2 = 1
    
    def login():
        global count1
        global count2
        try:
            mac = get_mac_entry()
            count2 = count1 +1
            start_tk.destroy()
        except ValueError as e:
            print(f"Login Failed: {e}")
            messagebox.showerror("Login Failed", e)
            return

    
    def pay():
        global count1
        global count2
        try:
            mac = get_mac_entry()
            amount = get_amount_entry()
            count1 = 1
        except ValueError as e:
            print(f"Payment Failed: {e}")
            messagebox.showerror("Payment Failed", e)
            return 


       
    def get_mac_entry():
        mac = mac_entry.get()
        # regex for mac
        mac_regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if re.match(mac_regex, mac):
            return mac.replace("-", ":")
        else:
            raise ValueError(f"Invalid MAC Address: {mac}")
    
    def get_amount_entry():
        amount = amount_entry.get()
        # regex for amount
        amount_regex = r"^[1-9]\d*$"
        if re.match(amount_regex, amount):
            return amount
        else:
            raise ValueError(f"Invalid Amount: {amount}")

    def end_tk():
        start_tk.destroy()
    
    

    start_tk = tk.Tk()
    start_tk.title("Game Registration/Login")

    # Create a label and entry widget for MAC Address
    mac_label = tk.Label(start_tk, text="MAC Address:")
    mac_label.grid(row=0, column=0)
    mac_entry = tk.Entry(start_tk)
    mac_entry.grid(row=0, column=1)

    mac_entry.insert(0, get_mac_address())

    # Create a label and entry widget for payment amount
    amount_label = tk.Label(start_tk, text="Amount (100/min):")
    amount_label.grid(row=2, column=0)
    amount_entry = tk.Entry(start_tk)
    amount_entry.grid(row=2, column=1)

    amount_entry.insert(0, "100")

    # Create Pay button
    pay_button = tk.Button(start_tk, text="Pay", command=pay)
    
    # Create Register and Login buttons
 
    login_button = tk.Button(start_tk, text="Login", command=login)


  
    pay_button.grid(row=3, column=1)
    login_button.grid(row=4, column=0, columnspan=2)

    start_tk.protocol("WM_DELETE_WINDOW", end_tk)
    start_tk.mainloop()
    return count2




def recv_msg():
    msg = conn.recv(SIZE).decode(FORMAT)
    if msg == "QUIT":
        conn.close()
    return msg



def handshake(nickname, mySnake):
    send(nickname)
    send(str(mySnake))


def receive():
    msg_len = int(conn.recv(HEADER).decode())
    msg = conn.recv(msg_len).decode()
    return msg.strip()


def send(msg):
    msg_len = str(len(msg.encode()))
    msg_len = msg_len.encode() + b" "*(HEADER-len(msg_len))
    conn.send(msg_len)
    conn.send(msg.encode())


def disconnected():
    print("[CONNECTION LOST]")
    _ = input("Your feedback is incredibly important:")
