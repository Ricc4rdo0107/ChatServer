import socket, sys, os
from threading import Thread
from pyfiglet import figlet_format
from _thread import start_new_thread
from socket import AF_INET, SOCK_STREAM
from rich.console import Console

console = Console()

class Server:

    def __init__(self):
        self.clients = []
        self.connected = {}


    def broadcast(self, msg, exclude=None, newline=True):
        if newline:
            msg_nice = msg
        else:
            msg_nice = msg.replace("\n", "")

        if ":" in msg_nice:
            console.print("[green]"+msg_nice.split(":")[0]+"[white]:"+msg_nice.split(":")[1]+"[/white]")
        elif "joined" in msg_nice:
            msm = msg_nice.split()
            msm[0] = "[green]"+msm[0]+"[/green]"

            for word in msm:
                if word != msm[-1]:
                    console.print(word+" ",end="")
                else:
                    console.print(word+" ",end="\n")

        else:
            print(msg_nice.replace("\n", ""))

        for client in self.clients:
            if exclude != None and client != exclude:
                client.send(msg_nice.encode())


    def handle(self, s):
        while True:
            conn, raddr = s.accept()
            self.clients.append(conn)
            console.print("[bold red]A new connection ha been established[/bold red]")

            new_thread = start_new_thread(self.threaded, (conn, raddr, ))


    def threaded(self, s, remote):
        name = str(f"{remote[0]}:{remote[1]}")
        mex_lenght = 10

        while True:
            s.send("Alias: ".encode())
            try:
                alias_data = s.recv(1024)
                if not alias_data: break
            except ConnectionResetError:
                self.connected.pop(alias_data.decode("cp850").replace("\n", ""))
                s.close()
                break
            except ConnectionAbortedError:
                try:
                    self.connected.pop(alias_data.decode("cp850").replace("\n", ""))
                except UnboundLocalError:
                    s.close()
                    break
                s.close()
                break
            
            if "\n" in alias_data.decode("cp850"):
                alias = alias_data.decode("cp850").replace("\n", "")
    
                if len(alias)>10:
                    s.send("Max Lenght is 10\n".encode())
                    continue
                elif alias.isspace():
                    s.send("You cant use a SPACE as name\n".encode())
                    continue
                elif alias == "":
                    s.send("Name cant be empy\n".encode())
                elif alias in self.connected:
                    s.send(f"Name ({alias}) alredy in use.\n".encode())
                else:
                    break

        try:
            self.connected.update({alias:s})
        except UnboundLocalError:
            s.close()
        else:
            self.broadcast(f"{alias} joined the chat!", newline=False)

        while True:
            try:
                data = s.recv(2048)
                if not data:
                    self.connected.pop(alias)
                    s.close()
                    self.connected.pop(alias)
                    break
                else:
                    data_D = data.decode("cp850")

            except Exception as e:
                try:
                    self.clients.remove(s)
                except ValueError:
                    break
                s.close()
                try:
                    self.connected.pop(alias)
                except KeyError:
                    s.close()
                    break
                except UnboundLocalError:
                    s.close()
                    break

            try:
                if data_D.replace("\n", "") != "":
                    self.broadcast(msg=f"{alias}: {data_D}", exclude=s)
                else:
                    pass
            except UnboundLocalError:
                s.close()
                self.connected.pop(alias)
                break


    def kick(self, alias):
        alias = alias.replace(" ", "").replace("\n", "")
        client = self.connected.get(alias)

        client.send("You got kicked!!!".encode())
        self.broadcast(msg=f"{alias} got kicked!")

        self.connected.pop(alias)
        client.close()

        
    def nice_exit(self):
        if input("Quit? Y/n ").lower() == "y" or input("Quit? Y/n ").lower() == "s":
            console.print("Shutting down...")
            if len(self.clients)>0:
                for client in self.clients:
                    client.send("Server closed.".encode())
                    client.close()
                    console.print(str(client) + " [red]removed[/red]")
                self.s.shutdown(1)
                self.s.close()
                sys.exit(0)
                exit()
        else:
            console.print("👍")
    

    def console(self, s):
        help = """
clients / list clients / list
kick {client}
"""
        while True:
            try:
                cmd = input("$ ")
            except (EOFError or KeyboardInterrupt):
                self.nice_exit()

            if cmd.lower() == "exit" or cmd.lower() == "quit":
                self.nice_exit()

            elif cmd.lower() == "clients" or cmd.lower() == "list clients" or cmd.lower() == "list":
                for client in list(self.connected.keys()):
                    print(client)

            elif cmd.startswith("kick"):
                try:
                    self.kick(cmd[4:])
                except:
                    print(f"Cannot kick : {cmd[4:]}")


    @staticmethod
    def display_startup_message():
        os.system("cls||clear")
        console.print("[bold green]"+figlet_format(text="Chat Server")+"[bold green]")
        console.print("[bold green]developed by [underline purple]Riccardo Zappitelli[underline purple]")


    def server(self, addr, port):
        self.display_startup_message()
        
        self.s = socket.socket(AF_INET, SOCK_STREAM)

        try:
            self.s.bind((addr, port))
        except OSError as e:
            print(F"Error:\n{e}")
            sys.exit()
        self.s.listen()
        console.print(f"[bold green]Listening on port [bold red]{port}[/bold red]")

        handle_Thread = Thread(target=self.handle, args=[self.s, ])
        console_Thread = Thread(target=self.console, args=[self.s, ])

        handle_Thread.start()
        console_Thread.start()




if __name__ == "__main__":
    s = Server()

    try:
        host, port = sys.argv[1], sys.argv[2]

        if not port.isdigit():
            print("Submit a valid port.")
            sys.exit()
        else:
            s.server(host, int(port))

    except IndexError:
        try:
            s.server(input("Host: "), int(input("Port: ")))
        except ValueError:
            print("Submit a valid port.")
            sys.exit()
        except KeyboardInterrupt:
            sys.exit()