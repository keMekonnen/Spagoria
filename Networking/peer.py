import threading
import socket
import traceback 
import time 
from colorama.ansi import Fore
import pickle
from pynput.keyboard import Listener
from hashlib import sha256
from Crypto.Cipher import AES

"""
BIG TODO 's
And handlers for cloud storage with appropriate checks and balances
"""

#Local Imports
from peerconnection import PeerConnection, PickleJar

class Peer:
    """
    Dundr Methods
    """
    def __init__(self, debug, serverport, allocatedMem=50, allocatedCPU=25, allocatedROM=50, local=False, myid=None, serverhost=None, maxpeers: int=15):
        self.peeradd = False
        self.doDebug = debug # boolean to decide wether or not there will be debugging will be active
        self.maxpeers = int(maxpeers) # limits the number of peers that can connect to a node
        self.full = False
        self.peerlimitreached = False # bool of wether or not the limit of peers is reached
        self.errs = {1: 'Incorrect Message type provided'} # dict of all the different types of peers
        self.serverport = int(serverport) # port to run the server on
        self.s = self.makeserversocket( self.serverport )
        if serverhost: # sets the server host for this node
            self.serverhost = serverhost
        else: 
            if local:
                self.serverhost = '127.0.0.1'
            else:
                self.identhost()
        if myid: #sets node ids
            self.myid = myid
        else: 
            self.myid = str('%s:%d' % (self.serverhost, self.serverport))

        self.workTypes = {}
        self.handlers = {'PING': self.pingHandle, 'PRNT': self.prntHandle, 'SRRY': self.missFail, 'STRG': self.strgHandle, 'AUTH': self.authHandle}
        self.peers = {}   
        self.shutdown = False  #bool over wether or not the node should shut down
        self.allocatedMem = allocatedMem #RAM allocated for the node, sets limit for how much the node can use before deleting subroccess, threads, work etc. In Megabytes
        self.allocatedCPU = allocatedCPU #Permitted cpu usage percentage sets limit for how much the node can use before deleting subroccess, threads, work etc. In Percentage
        self.allocatedROM = allocatedROM #Permitted ROM for the node, sets limit for how much the node can use before refusing more. In Megabytes
        self.occupied = False # bool over wether or not the peer has recieved work already
    def __str__(self) -> str:
        return str(self.myid)

    """
    Handlers
    """
    def missFail(self, peerconn, msgdata):
        self.debug('There has been an error with : '+Fore.YELLOW+str(peerconn)+Fore.WHITE+Fore.RED +" "+msgdata + Fore.WHITE)
    def pingHandle(self, peerconn, msgdata):
        pass  
    def prntHandle(self, peerconn, msgdata):
        self.debug(str(peerconn)+' says: '+msgdata)
    def authHandle(self, peerconn, msgdata):
        pass
    def strgHandle(self, peerconn, msgdata):
        try:
            p: PickleJar = pickle.loads(msgdata)
        except:
            p = pickle.loads(msgdata)
            if self.doDebug:
                self.doDebug(Fore.YELLOW + "Warning: PickleJar not recieved for strgHandle"+ Fore.WHITE)
        if type(p) == "<class 'peerconnection.PickleJar'>":
            try:
                if not self.occupied:
                    PeerHands = []
                    for i in p.pickles:
                        i = pickle.loads(i)
                        PeerHands.append(i)
                    cStorage = self.runstorage(PeerHands[0])
                    self.occupied = True
                    try: 
                        cStorage.run(self.s)
                    except:
                        addon = ''
                        if self.doDebug: traceback.print_exc()
                        else: addon += Fore.YELLOW +' set debug to True for details' + Fore.WHITE
                        self.missFail(peerconn, 'Faliure handling work'+addon)
                    finally:
                        self.occupied = False
                        self.prntHandle(peerconn, 'Storage Job completed')

                else:
                    self.missFail(peerconn, 'Peer is already working')    
            except:
                addon = ''
                if self.doDebug: traceback.print_exc()
                else: addon += Fore.YELLOW +' set debug to True for details' + Fore.WHITE
                self.missFail(peerconn, 'Faliure handling storage request '+addon)
    """
    Misc. Methods
    """
    
    def debug(self, inp, err:bool=False):
        #fancy print function, mostly useless, aesthetically pleasing
        if self.doDebug:
            try:
                if err:
                    print ("[%s] %s" % ( str(threading.currentThread().getName()), Fore.RED + "Err: "+inp+ Fore.WHITE))
                else:
                    print ("[%s] %s" % ( str(threading.currentThread().getName()), inp))
            except:
                print(inp)
    def makeserversocket(self, port):
        #tintintin
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        s.bind( ( '', port ) )
        s.listen()
        return s
    def identhost(self):
        #NOTE this maybe the most worthless function ive ever written
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.connect(('google.com', 80))
        self.serverhost = s.getsockname()[0]
        s.close()
    """
    Stabilization Methods    
    """
    def stabilize(self):
        # makes sure all the peers are live, by pinging them, thus 'stabilizing' the network
        # it runs aslong as the node isnt instructed to shut down
        def stabilizer():
            todelete = []
            self.peeradd = False
            try:
                for pid in self.peers:
                    try:
                        self.debug( 'Check live %s' % pid )
                        host, port = self.peers[pid]
                        peerconn = PeerConnection(pid, host, port)
                        peerconn.senddata( 'PING', {} )
                    except:
                        self.debug('%s is not live' % str(pid))
                        todelete.append(pid)
                        peerconn = False
                    try:
                        for pid in todelete: 
                            if pid in self.peers: del self.peers[pid]
                    finally:
                        if peerconn:
                            peerconn.close()
            except RuntimeError:
                stabilizer()
            if len(self.peers) < self.maxpeers:
                self.peeradd = True
        def runstabilzer(delay=15.0):
            while not self.shutdown:
                time.sleep(delay)
                stabilizer()
        t = threading.Thread(target=runstabilzer)
        t.start()
    def addpeer(self, pid, host:str, port:int):
        # makes sure adding a peer does not interrupt and crash the stabilization of the existing peers
        hpTuple = (host, port)
        def runaddpeer(hpTuple, pid):
            try:
                if len(self.peers) > self.maxpeers:
                    if not self.peerlimitreached:
                        self.debug("Max peer limit reached. Connection with |"+ str(hpTuple)+"| has failed", err= True)
                    self.peerlimitreached = True
                elif self.peeradd and self.maxpeers > len(self.peers):
                    self.peers[pid] = hpTuple
                    return True
                elif not self.peeradd and len(self.peers) < self.maxpeers:
                    time.sleep(2)
                    runaddpeer(hpTuple, pid)
                    return True
    

            except:
                if self.doDebug:
                    traceback.print_exc()
                return False
        t = threading.Thread(target= runaddpeer, args=[hpTuple, pid])
        t.start()
    """
    Comm Methods
    """
    def mainloop(self, debug):
        #creates the loop that listens for new connections
        self.debug( 'Server started: %s (%s:%d)' % ( self.myid, self.serverhost, self.serverport ) )
        displayedPause = 0
        self.stabilize()
        while not self.shutdown :
            try:
                if not self.occupied and not self.peerlimitreached:
                    self.s.listen()
                    self.debug( 'Listening for connections...' )
                    clientsock, clientaddr = self.s.accept()
                    self.debug('Connected to: %s' % (str(clientaddr)))
                    clientsock.settimeout(None)
                    t = threading.Thread( target = self.handlepeer, args = [ clientsock, debug ] )
                    t.start()
                else:
                    if displayedPause == 0:
                        self.debug('Work Recieved,  Mainloop Paused')
                        displayedPause += 1
            except:
                if self.doDebug:
                    traceback.print_exc()
                    continue
        self.debug( 'Main loop exiting' )
        self.s.close()
    
    def handlepeer(self, clientsock: socket, debug):
        #This function is too annoying for me to bother explaining
        self.debug( 'Connected ' + str(clientsock.getpeername()))
        host, port = clientsock.getpeername()
        peerconn = PeerConnection( host, port, sock=clientsock, debug=debug )
        self.addpeer(peerconn.id, host, port)
        try: 
            msg = peerconn.recvdata()
            msgtype = msg[0:4]
            msgdata = msg[5:len(msg)]
            if msgtype: msgtype = msgtype.upper()
            if msgtype not in self.handlers and msgtype !='':
                msgdata = '%s msgtype given by: %s does not exist' % msgtype, peerconn
                msgtype = 'SRRY'
                self.handlers[ msgtype ]( peerconn, msgdata )
            elif msgtype == '':
                msgtype = 'SRRY'
                msgdata = 'msgtype has not been provided by %s' % str(peerconn)
                self.handlers[ msgtype ]( peerconn, msgdata )
            else:
                self.handlers[ msgtype ]( peerconn, msgdata )
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
    """
    Command Recognition Methods
    """
    def recCommand(self):
        try:
            lines = open('./inputFile.txt', 'r').readlines()
            msgargs = {'PRNT': self.prnt, 'STRG': self.strg, 'PING':self.ping}
            
            print(lines)
            msgtype = lines[0][:-1]
            msgtype = msgtype.upper()
            if msgtype not in msgargs:
                print(Fore.RED+ "there is no message type called: ", msgtype+ Fore.WHITE)
                return False
            msgdata = msgargs[msgtype](lines=lines)
            if msgdata == list(msgdata):
                msgdata = msgdata[0]
            host = (lines[-2])[0:-1]
            port = int(lines[-1])
            print((host, port))
            peerconn = PeerConnection(host, port)
            peerconn.senddata(msgtype, msgdata)
        except FileNotFoundError:
            print(Fore.RED+"input file not found. make sure it is created and filled properly"+Fore.WHITE)
        except :
            if self.doDebug:
                traceback.print_exc()
            return False
    def prnt(self, lines:list):
        inpMessage = str(lines[1])
        return {"strMsg": inpMessage}
    def strg(self, lines:list):
        file_path = input("file path:")
        try:
            fl = open(file_path, 'rb')
            key = sha256(input("password:").encode()).digest()
            f = fl.read()
            cipher = AES.new(key, AES.MODE_EAX)
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(f)
            return [{'file': ciphertext}, [nonce, tag]]
        except FileNotFoundError:
            print(Fore.RED+ "there is no file called: ", file_path+ Fore.WHITE)
    def ping(self, lines):
        return {'ping': None}