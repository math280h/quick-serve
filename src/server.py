import socket
import threading


def expected_args(cmd, n):
    return len(cmd) >= n


class Server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 80
        self.size = 1024
        self.words = {}
        # Bind Socket & set Socket Options
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        # Wait for a connection (Max 5 in queue allowed)
        self.sock.listen(5)
        while True:
            # Accept connection
            client, address = self.sock.accept()
            # Split connection into thread
            threading.Thread(target=self.handle_client, args=(client, address)).start()

    def handle_client(self, conn, address):
        while True:
            # Recieve Data
            try:
                data = conn.recv(self.size)
            except (ConnectionResetError, ConnectionAbortedError) as e:
                print("Connection was closed by client")
                break
            if not data:
                break

            # Decode Data
            try:
                command = data.decode('UTF-8').strip().split()
            except UnicodeDecodeError as e:
                print("Error: " + e.reason)
                conn.send("ERROR invalid command\n".encode())

            # Make sure there is a command
            if len(command) == 0 or command[0] == '':
                conn.send("ERROR invalid command\n".encode())

            # Check for specific commands
            print("New Command: " + str(command))
            if command[0] == 'GET' and expected_args(command, 2) and command[1] != '':
                # Get a word description
                if command[1] in self.words:
                    answer = "ANSWER " + self.words[command[1]] + "\n"
                    conn.send(answer.encode())
                else:
                    conn.send("ERROR undefined\n".encode())
            elif command[0] == 'SET' and expected_args(command, 3) and command[1] != '' and command[2] != '':
                # Set a new word and it's description
                if command[1] not in self.words:
                    desc = ""
                    for i, d in enumerate(command):
                        if i != 0 and i != 1:
                            if i == 2:
                                desc += d
                            else:
                                desc += " " + d
                    self.words[command[1]] = desc
                    conn.send("OK saved word description\n".encode())
                else:
                    conn.send("ERROR already defined\n".encode())
            elif command[0] == 'CLEAR':
                # Clear all currently stored words
                self.words = {}
                conn.send("OK cleared all descriptions\n".encode())
            elif command[0] == 'ALL':
                # List all words
                if len(self.words) == 0:
                    conn.send("ERROR no stored words\n".encode())
                else:
                    conn.send("OK all stored words below\n".encode())
                    for w in self.words.keys():
                        msg = w + " " + self.words[w] + "\n"
                        conn.send(msg.encode())
            else:
                conn.send("ERROR invalid command\n".encode())


if __name__ == '__main__':
    Server().listen()
