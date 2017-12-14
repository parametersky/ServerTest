import socket
import json
import os
import sys
from threading import Thread
from multiprocessing import Process
from queue import Queue
class SocketThread(Thread):
    def __init__(self,thread_name,sock):
        Thread.__init__(self,name=thread_name)
        self.sock = sock
        self.work = True
    def run(self):
        while self.work:
            data = self.sock.recv(1024)
            print(data)
            str_data = str(data,encoding='utf-8')
            if str_data.startswith("test ok"):
                self.send(b'this test is right')
            if len(data) == 0:
                self.work=False
                self.sock.close()

    def stop(self):
        self.work = False

    def send(self,mesg):
        print('send message',mesg)
        if self.work:
            self.sock.sendall(mesg)

class MySocketServer():
    class _SocketServer:
        def __init__(self):
            print('_SocketServer init')
            self.serverRun = False
            self.msg_queue = Queue(maxsize=10000)
            self.workThread = Thread(target=self.handleMessage)
            self.socketlist = {}
        def handleMessage(self,mesg):
            print('handle message')
            msg = json.loads(mesg,encoding='utf-8')
            print("handle Message ",msg)
            serial = msg['serial']
            uid = msg['uid']
            print(self.socketlist)
            sock = self.socketlist.get(serial)
            if sock:
                sock.send(bytes('{"uid": "%s", "username":"test"}\n' % uid ,encoding="utf8"))
            else:
                print('cannot find socket by serial: ',serial)

        def putMsg(self,msg):
            print('put mesg',msg)
            self.msg_queue.put(msg)

        def startWork(self):
            t = Thread(target=self.consuming)
            t.start()
        def consuming(self):
            print('start work')
            import pika
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()
            channel.queue_declare(queue='hello')

            def callback(ch, method, properties, body):
                print("callback body: ",body)
                bodyy=str(body,encoding='utf8')
                self.handleMessage(bodyy)
            channel.basic_consume(callback, queue='hello', no_ack=True)
            channel.start_consuming()
      #  def startWork(self):
       #     print('start work')
        #    self.workThread.start()
        def stopWork(self):
            self.isWork = False
            self.workThread.join()
        def runServer(self):
            self.process= Thread(target=self.runsocketserver)
            self.process.start()
            self.serverRun = True

        def runsocketserver(self):
            print('run socket server5')
            server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            print('run socket server4')
            server_socket.bind(("0.0.0.0",8001))
            print('run socket server3')
            server_socket.listen(500)
            print('run socket server2')
            while True:
                print('run socket server1')
                sock,addr = server_socket.accept()
                data = sock.recv(1024)
                print('data:', data)
                info = json.loads(str(data, encoding='utf-8'))
                print('serail: ', info['serial'])
                serial = info['serial']
                sothread = SocketThread(str(serial),sock)
                sothread.start()
                solist = self.socketlist
                solist[serial] = sothread
                print("socket list ",solist)

    _INSTANCE = None
    def __init__(self):
        if not MySocketServer._INSTANCE:
            print("init _SocketServer")
            MySocketServer._INSTANCE = MySocketServer._SocketServer()
            #MySocketServer._INSTANCE.cls = self
        else:
            print('instance is read')
    def putMsg(self,msg):
        print("put Msg")
        MySocketServer._INSTANCE.putMsg(msg)
    def runServer(self):
        MySocketServer._INSTANCE.runServer()
    def startWork(self):
        MySocketServer._INSTANCE.startWork()
        
def resetOutput(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    for f in sys.stdout, sys.stderr: f.flush()
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())  # dup2函数原子化关闭和复制文件描述符
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
resetOutput(stdout='/home/ubuntu/socket-server/log-file',stderr='/home/ubuntu/socket-server/error-file')
mySocketServer = MySocketServer()
mySocketServer.runServer()
mySocketServer.startWork()








