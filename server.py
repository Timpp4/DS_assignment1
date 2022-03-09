import atexit
import socket
import threading

users = {}
addresses = {}

def main():
    # Closes client sockets at termination
    atexit.register(cleanup)
    # Server address
    host = "localhost"
    port = 9999
    # Create socket that uses IPv4 and TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    print("Listening @ {}:{}".format(host, port))
    # Thread for new connection
    connThread = threading.Thread(target=connectionThread, args=(s,))
    connThread.start()
    connThread.join()
    #  Closes client sockets
    cleanup()
    # Closes server socket
    s.close()
    print("Server is offline.")

def connectionThread(sock):
    # Accept connection and add client data to dictionary
    while True:
        try:
            client, address = sock.accept()
        except Exception:
            print("Something went wrong... (connectionThread)")
            break
        print("{} has connected.".format(address[0]))
        addresses[client] = address
        threading.Thread(target=clientThread, args=(client,)).start()

def clientThread(client):
    # Client logic server side
    address = addresses[client][0]
    try:
        user = getNickname(client)
    except Exception:
        print("Something went wrong... (getNickname {})".format(address))
        del addresses[client]
        client.close()
        return
    print("{} is now known as {}".format(address, user))
    users[client] = user
    try:
        client.send("Hello {}! You can now start chatting. Type \"/help\" for help ;)".format(user).encode("utf8"))
    except Exception:
        print("Connection lost {} ({}).".format(address, user))
        del addresses[client]
        del users[client]
        client.close()
        return
    broadcast("{} is now online.".format(user))

    while True:
        try:
            message = client.recv(2048).decode("utf8")
            if message == "/quit":
                client.send("You are now offline.".encode("utf8"))
                del addresses[client]
                del users[client]
                client.close()
                print("{} ({}) is now offline.".format(address, user))
                broadcast("{} is now offline.".format(user))
                break
            elif message == "/online":
                onlineUsers = ', '.join([user for user in sorted(users.values())])
                client.send("Users online: {}".format(onlineUsers).encode("utf8"))
            elif message == "/help":
                client.send("""
            You can send a message simply by typing it and hitting ENTER.
            Available commands:
            /help\tDisplay all available commands
            /online\tDisplay current online users
            /private\tSend a private message, usage: /private <user> <message>
            /quit\tGracefully disconnect from the chat""".encode("utf8"))
            #################################################################################
            elif message.split()[0] == "/private":
                # get target user address
                targetUser = getAddress(message.split()[1])
                privateMessage = ' '.join(message.split()[2:])
                print("{} ({} PRIVATE-> {}): {}".format(address, user, message.split()[1], privateMessage))
                targetUser.send("(PRIVATE) {}: {}".format(user, privateMessage).encode("utf8"))
                client.send("(PRIVATE) {}: {}".format(user, privateMessage).encode("utf8"))
            else:
                print("{} ({}): {}".format(address, user, message))
                broadcast(message, user)
        except Exception:
            print("{} ({}) is now offline.".format(address, user))
            del addresses[client]
            del users[client]
            client.close()
            broadcast("{} is now offline.".format(user))
            break

def getNickname(client):
    client.send("Set a nickname: ".encode("utf8"))
    nickname = client.recv(2048).decode("utf8")
    alreadyTaken = False
    if nickname in users.values():
        alreadyTaken = True
        while alreadyTaken:
            client.send("Nickname taken. Choose another one: ".encode("utf8"))
            nickname = client.recv(2048).decode("utf8")
            if nickname not in users.values():
                alreadyTaken = False
    return nickname

def getAddress(nickname):
    for key, value in users.items():
        if nickname == value:
            return key
    return "User '{}' not found".format(nickname)


def broadcast(message, sentBy = ""):
    try:
        if sentBy == "": # online/offline messages
            for user in users:
                user.send(message.encode("utf8"))
        else: # user messages
            for user in users:
                user.send("{}: {}".format(sentBy, message).encode("utf8"))
    except Exception:
        print("Something went wrong... (broadcast)")

def cleanup():
    if len(addresses) != 0:
        for sock in addresses.keys():
            sock.close()
    print("Cleanup done.")

main()