import traceback
from threading import Thread
import socket
import random
import string
import time


otp_code = ''.join([random.choice(string.ascii_lowercase) for _ in range(6)])

def update_code():
    while True:
        time.sleep(5)
        print('code updated')
        global otp_code
        otp_code = ''.join([random.choice(string.ascii_lowercase) for _ in range(6)])

def client_thread(conn: socket, ip: str, port: str) -> None:
    try:
        global otp_code
        conn.sendall(otp_code.encode())
    except:
        conn.close()
        print('Connection', ip, ':', port, 'close')

def start_server(host: str, port: int) -> None:
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        soc.bind((host, port))
        print('Socket bind complete')
    except socket.error:
        import sys
        print('Bind failed.')
        sys.exit()

    #Start updater
    Thread(target=update_code).start()
    #Start listening on socket
    soc.listen(300)
    print('Socket now listening')
    while True:
        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        conn.settimeout(60)
        print('Accepting connection from', ip, ':', port)
        try:
            Thread(target=client_thread, args=(conn, ip, port)).start()
        except:
            print("Thread error!")
            traceback.print_exc()
    soc.close()

if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print('Usage:', sys.argv[0], '<ip> <port>')
    #     exit(0)
    host = "127.0.0.1"
    port = 1337

    start_server(host, port)  