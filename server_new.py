import socket
import json
import os
import sys
from threading import Thread
from multiprocessing import Process
from queue import Queue
from logging import Formatter,getLogger,FileHandler
from logging.handlers import TimedRotatingFileHandler,RotatingFileHandler
import logging

from functools import reduce
def getRotateHandler(dir):
    rotating_handler = FileHandler(dir)
    rotating_handler.setLevel(logging.INFO)
    rotating_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
        '[%(filename)s:%(lineno)d]'))
    return rotating_handler
def getErrorHandler(dir):
    error_handler = TimedRotatingFileHandler(dir,'D',1)
    error_handler.setLevel(logging.DEBUG)
    error_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
        '[%(filename)s:%(lineno)d]'))
    return error_handler
logg = logging.getLogger(__name__)
logg.setLevel(logging.DEBUG)
logg.addHandler(getErrorHandler("/var/log/socket-server/socketserver.log"))


def addStr(str1,str2):
    return str(str1)+' '+str(str2)
def logi(*args):
    string = reduce(addStr,args,"")
    logg.log(logging.INFO,string)
    print(string)
def logd(*args):
    string = reduce(addStr, args, "")
    logg.log(logging.DEBUG,string)



class SocketThread(Thread):
    def __init__(self, thread_name, sock):
        Thread.__init__(self, name=thread_name)
        self.sock = sock
        self.work = True


    def run(self):
        while self.work:
            data = self.sock.recv(1024)
            logi('recive data',data)
            str_data = str(data, encoding='utf-8')
            if str_data.startswith("test ok"):
                self.send(b'this test is right')
            if len(data) == 0:
                self.work = False
                self.sock.close()
		

    def stop(self):
        self.work = False

    def send(self, mesg):
        logi('send message')
        if self.work:
            self.sock.sendall(mesg)
        else:
            logi('thread not work')


class MySocketServer():
    class _SocketServer:
        def __init__(self):
            self.serverRun = False
            self.msg_queue = Queue()
            self.workThread = Thread(target=self.handleMessage)
            self.socketlist = {}
            # self.runsocketserver()

        def handleMessage(self,mesg):
            logi('handle message',mesg)
            mesg = str(mesg,encoding='utf8')
            msg = json.loads(mesg,encoding='utf-8')
            logi('handle message 1')
            serial = msg['serial']
            logi('handle message 2')
            uid = msg['uid']
            logi('handle message 3')
            logi(self.socketlist)
            logi('handle message 4')
            sock = self.socketlist.get(serial)
            logi('handle message 5')
            if sock:
                logi('send message to socket')
                sock.send(bytes('{"uid": "%s", "username":"test"}\n' % uid ,encoding="utf8"))
            else:
                logi('cannot find socket by serial: ', serial)

        def putMsg(self, msg):
            logi('put mesg', msg)
            self.msg_queue.put(msg)

        def startWork(self):
            t = Thread(target=self.consuming)
            t.start()
        def consuming(self):
            logi('start work')
            import pika
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',heartbeat=0))
            channel = connection.channel()
            channel.queue_declare(queue='hello')

            def callback(ch, method, properties, body):
                logi("callback body: ",body)
                self.handleMessage(body)
            channel.basic_consume(callback, queue='hello', no_ack=True)
            channel.start_consuming()

        def stopWork(self):
            self.isWork = False
            self.workThread.join()

        def runServer(self):
            if self.serverRun:
                return
            self.process = Thread(target=self.runsocketserver)
            self.process.start()
            self.serverRun = True

        def runsocketserver(self):
            logi('runsocketserver start')
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logi('runsocketserver build socket done')
            server_socket.bind(("0.0.0.0", 8001))
            logi('runsocketserver bind socket done')
            server_socket.listen(5)
            logi('runsocketserver listen socket done')
            while True:
                logi('runsocket server while 1')
                sock, addr = server_socket.accept()
                logi('runsocket server while 2')
                try:
                    data = sock.recv(1024)
                except Exception as error:
                    logi(error)
                    continue
                logi('runsocket server while 3')
                logi('data:', data)
                if len(data) == 0:
                    continue
                try:
                    info = json.loads(str(data, encoding='utf-8'))
                except Exception as error:
                    logi(error)
                    continue
                logi('serail: ', info['serial'])
                serial = info['serial']
                sothread = SocketThread(str(serial), sock)
                sothread.start()
                solist = self.socketlist
                solist[serial] = sothread
                logi("socket list ", solist)
                logi('runsocket server while 4')

    _INSTANCE = None

    def __init__(self):
        if not MySocketServer._INSTANCE:
            logi("init _SocketServer")
            MySocketServer._INSTANCE = MySocketServer._SocketServer()
            MySocketServer._INSTANCE.cls = self
        else:
            logi('instance is read')

    def putMsg(self, msg):
        logi("put Msg")
        MySocketServer._INSTANCE.putMsg(msg)

    def runServer(self):
        MySocketServer._INSTANCE.runServer()
    def runSocketServer(self):
        MySocketServer._INSTANCE.runsocketserver()

    def startWork(self):
        MySocketServer._INSTANCE.startWork()


def resetOutput(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    for f in sys.stdout, sys.stderr: f.flush()
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

try:
    mySocketServer = MySocketServer()
    mySocketServer.startWork()
    mySocketServer.runSocketServer()
except Exception as error:
    logg.exception(error)
