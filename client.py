import socket
import threading
import datetime
import colorama
import sys

# Initialize
clientIsAlive = True

def main():
    global clientIsAlive
    # Windows compatibility - colorama
    # https://pypi.org/project/colorama/
    colorama.init()
    # Server address
    host = input("Input chat server's IP: ")
    if host == "":
        host = "localhost"
    port = 9999
    print("Trying to connect {}:{}".format(host, port))
    # Create socket that uses IPv4 and TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    # Threads for sending & receiving messages
    sendingThread = threading.Thread(target=send, args=(s,))
    receivingThread = threading.Thread(target=receive, args=(s,))
    sendingThread.start()
    receivingThread.start()
    # check for timeout
    while receivingThread.is_alive() and sendingThread.is_alive():
        continue
    clientIsAlive = False
    s.close()
    print("\nGoodbye!")

def currentTime():
    time = datetime.datetime.now().strftime("%H:%M:%S")
    return time

def deleteLastLine():
    # ANSI escape codes (to simplify terminal output)
    # https://tforgione.fr/posts/ansi-escape-codes/
    sys.stdout.write("\x1B[A") # Up one line
    sys.stdout.write("\x1B[2K") # Delete the line

def send(sock):
    while clientIsAlive:
        try:
            message = input()
            deleteLastLine()
            sock.send(message.encode("utf8"))
        except Exception:
            print("Error while sending a message.")
            break

def receive(sock):
    while clientIsAlive:
        try:
            message = sock.recv(2048).decode()
            if message:
                print("[{}] {}".format(currentTime(), message))
            else:
                break
        except Exception:
            print("Lost connection to the server.")
            break

main()