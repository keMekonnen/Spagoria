import threading
import socket
import traceback 
import time 
from colorama.ansi import Fore # to make the debugging look ~nice
import pickle

#Local Imports
from peerconnection import PeerAuth, PeerConnection

class RecvdPeer:
    # NOTE idk what this is yet just bear with me yo
    def __init__(self, peerconn: PeerConnection):
        host = peerconn.host
        port = peerconn.port
        self.address=(host, port)
        self.id = peerconn.id
        Auth = PeerAuth(self) #This class doesnt exist yet, ik ik ... TODO(keMekonnen)
        # self.DH = (Auth.sharedPrime, Auth.sharedBase) 
        ######################### Which is best, should we stick with basic Diffie-Hellman or should we allow for other options to be devd? Find out next time on Total Dramaaa IsllAANDDD!!!
        # self.DH = (Auth.dh.sharedPrime, Auth.dh.sharedBase) 


class Peer:
    """
    Dundr Methods
    """
    def __init__(self, debug, serverport, allocatedMem=50, allocatedCPU=25, allocatedROM=50, local=False, myid=None, serverhost=None, maxpeers=5):
        self.peeradd = False
        self.doDebug = debug # boolean to decide wether or not there will be debugging will be active
        self.maxpeers = int(maxpeers) # limits the number of peers that can connect to a node
        self.errs = {1: 'Incorrect Message type provided'} # dict of all the different types of peers
        self.serverport = int(serverport) # port to run the server on
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
        self.handlers = {'PING': self.pingHandle, 'PRNT': self.prntHandle, 'SRRY': self.missFail}
        self.peers = [{},{},{}]         #list of dicts for all the peers that this peer can connect to. 
                                         #peers[0] is a dict of Routing Nodes that are authorized to assign work, and add new routing nodes, must not be empty #NOTE idk what a routing node is too
                                         #peers[1] is a dict of nodes assigned with a BCNN task with this node, can be empty
                                         #peers[2] is a dict of nodes asigned with a CBWH task with this node, can be empty
                 #NOTE ^^^^^ This may ultimately be a useless, considering ive had it in here for the past two weeks and did nothing with them...
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
    def srryHandle(self, peerconn, msgdata):
        self.debug('There has been an error with : '+Fore.YELLOW+str(peerconn)+Fore.WHITE+Fore.RED +" "+msgdata + Fore.WHITE)
    def pingHandle(self, peerconn, msgdata):
        pass  
    def prntHandle(self, peerconn, msgdata):
        self.debug(str(peerconn)+' says: '+msgdata) #prints out the sent message #NOTE just realized how pointless this comment is
    def workHandle(self, peerconn, msgdata):
        try:
            if not self.occupied:
                recvP = RecvdPeer(peerconn)
                #TODO(keMekonnen) Stop fcking procrastinating and fix this
            else:
                self.srryHandle(peerconn, 'Peer is already working')    
        except:
            self.srryHandle(peerconn, 'Work Handling Failed')
            if self.doDebug:
                traceback.print_exc()
    """
    Misc. Methods
    """
    def debug(self, inp):
        #fancy print function, mostly useless, aesthetically pleasing
        if self.doDebug:
            print ("[%s] %s" % ( str(threading.currentThread().getName()), inp))
        self.prevdebugmsg = inp
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
            for pid in self.peers:
                try:
                    self.debug( 'Check live %s' % pid )
                    host, port = self.peers[pid]
                    peerconn = PeerConnection(pid, host, port)
                    peerconn.senddata( 'PING', {} )
                except:
                    self.debug('%s is not live' % str(pid))
                    todelete.append(pid)
                try:
                    for pid in todelete: 
                        if pid in self.peers: del self.peers[pid]
                finally:
                    if peerconn:
                        peerconn.close()
            self.peeradd = True
        def runstabilzer(delay=45.0):
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
                if self.peeradd:
                    self.peers[pid] = hpTuple
                    return True
                else:
                    runaddpeer(hpTuple, pid)
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
        s = self.makeserversocket( self.serverport )
        self.debug( 'Server started: %s (%s:%d)' % ( self.myid, self.serverhost, self.serverport ) )
        self.stabilize()
        while not self.shutdown:
            try:
                s.listen()
                self.debug( 'Listening for connections...' )
                clientsock, clientaddr = s.accept()
                self.debug('Connected to: %s' % (clientaddr))
                clientsock.settimeout(None)
                t = threading.Thread( target = self.handlepeer, args = [ clientsock, debug ] )
                t.start()
            except KeyboardInterrupt: #TODO(keMekonnen) figure out why this is not working
                print('KeyboardInterrupt: stopping mainloop')
                self.shutdown = True
                continue
            except:
                if self.doDebug:
                    traceback.print_exc()
                    continue
        self.debug( 'Main loop exiting' )
        s.close()
    def handlepeer(self, clientsock, debug):
        #This function is too annoying for me to bother explaining
        self.debug( 'Connected ' + str(clientsock.getpeername()))
        host, port = clientsock.getpeername()
        peerconn = PeerConnection( None, host, port, clientsock, debug=debug )
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
                self.debug( Fore.BLUE + 'Handling peer msg: %s' % msgtype + '' + Fore.WHITE)
                self.handlers[ msgtype ]( peerconn, msgdata )
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
