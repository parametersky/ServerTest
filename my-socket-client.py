import socket
from threading import Thread
import time
def test():
    mysocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # mysocket.connect(('sdm.gongyuanhezi.com',8001))
    mysocket.connect(('localhost',8001))

    mysocket.sendall(b'{"serial":123456}')
    print('send message')
    def test():
        while True:
            data=mysocket.recv(1024)
            print('Received',repr(data))
            if len(data) == 0:
                mysocket.close()

    def send():
        while True:
            mysocket.send(b'{"serial":123456}')
            time.sleep(5)

    thre = Thread(name="test",target=test)

    thre.start()
    sen = Thread(name="send",target=send)
    sen.start()

    return mysocket

if __name__ == "__main__":
    try:
        mysocket = test()
    except KeyboardInterrupt:
        mysocket.close()


