import socket
import traceback
import time
import pickle
from colorama.ansi import Fore
from random import random

class messagedata:
        def __init__(self, msgtype: str, data: dict):
                self.msgtype = msgtype.upper()
                self.msg = self.createmsgdata(data)
        def createmsgdata(self, inp: dict):
                if self.msgtype == 'STRG':        
                        return self.makemsgSTRG(inp["file"], inp["fileName"])
                elif self.msgtype == 'SRRY' or self.msgtype == 'PRNT':
                        return self.makemsgSTR(inp["strMsg"])
                elif self.msgtype == 'PING':
                        return self.makemsgPING()
        def makemsgSTR(self, msg):
                msg = self.msgtype+":"+str(msg)
                return msg
        def makemsgSTRG(self, data, name):
                pickles = []
                pickles.append(data)
                pickles.append(name)
                jar = PickleJar(pickles)
                msg = self.msgtype+":"+pickle.dumps(jar)
                return msg
        def makemsgPING(self):
                return self.msgtype+":"


class PeerConnection:
        def __init__( self, host, port, sock=False, debug=False, peerid=None ):
                if peerid:
                        self.id = peerid
                else:
                        self.id = (host, port)
                self.doDebug = debug
                self.host  = host
                self.port = port
                if not sock:
                        self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                        self.s.connect( ( host, int(port) ) )
                else:
                        self.s = sock
        def __str__(self) -> str:
                return "|%s|" % str(self.id)
        def close( self ):
                        self.s.close()
                        self.s = None
        def makemsg(self, msgtype, msgdata: dict):
                try:
                        if msgtype and len(msgtype) == 4:
                                msg = messagedata(msgtype, msgdata).msg
                                return msg
                        else:
                                return "SRRY:Improper msgtype provided"
                except:
                        addon = ''
                        if self.doDebug: traceback.print_exc()
                        else: addon += Fore.YELLOW +' set debug to True for details' + Fore.WHITE
                        return 'SRRY:Faliure makingmsg'+addon
        def senddata(self, msgtype, msgdata: dict):
                try:
                        msg = self.makemsg(msgtype, msgdata)
                        l = str(len(msg)).encode()
                        self.s.send(l)
                        time.sleep(0.5)
                        self.s.sendall(msg.encode())
                except:
                        addon = ''
                        if self.doDebug: traceback.print_exc()
                        else: addon += Fore.YELLOW +' set debug to True for details' + Fore.WHITE
                        return 'SRRY:Failure sending data'+addon
        def recvdata(self):
                try:
                        l = self.s.recv(1024).decode() # this may be a problem in the future, but if file's size is to big to recive with 2k bytes, fuck it
                        msg = self.s.recv(int(l)).decode()
                        time.sleep(0.5)
                        return msg
                except:
                        addon = ''
                        if self.doDebug: traceback.print_exc()
                        else: addon += Fore.YELLOW +' set peerconn debug to True for details'
                        return 'SRRY:Failure reciving data'+addon
        

class PickleJar:
        def __init__(self, pickles: list) -> None:
                self.pickles = pickles