import socket
import traceback
import threading
from colorama.ansi import Fore
#Local Imports
from peerconnection import PeerConnection
from shrtHand import shrtHand

# #TODO[kaMekonnen] make this do thing
# class cloudStorage:
#     def __init__(self, AuthMain: shrtHand, AuthSecondary: shrtHand, BackupAuths: list, doDebug: bool = False):
#         self.AuthMain = AuthMain
#         self.AuthSecondary = AuthSecondary
#         self.BackupDicts = BackupAuths
#         self.shutdown = False
#         self.doDebug = doDebug
#         self.handlers = {}
#     def run(self, socket: socket):
#         while not self.shutdown:
#             socket.listen()
#             clientsock, clientaddr = self.s.accept()
#             self.debug('Connected to: %s' % (clientaddr))
#             clientsock.settimeout(None)
#             # clientsock.settimeout(None)
#             t = threading.Thread( target = self.handlepeer, args = [clientsock] )
#             t.start()
#     def debug(self, inp):
#         #fancy print function, mostly useless, aesthetically pleasing
#         if self.doDebug:
#             print ("[%s] %s" % ( str(threading.currentThread().getName()), inp))
#         self.prevdebugmsg = inp
#     def handlepeer(self, clientsock, debug):
#         self.debug( 'Connected ' + str(clientsock.getpeername()))
#         host, port = clientsock.getpeername()
#         peerconn = PeerConnection( None, host, port, clientsock, debug=debug )
#         self.addpeer(peerconn.id, host, port)
#         try: 
#             msg = peerconn.recvdata()
#             msgtype = msg[0:4]
#             msgdata = msg[5:len(msg)]
#             if msgtype: msgtype = msgtype.upper()
#             if msgtype not in self.handlers and msgtype !='':
#                 msgdata = '%s msgtype given by: %s does not exist' % msgtype, peerconn
#                 msgtype = 'SRRY'
#                 self.handlers[ msgtype ]( peerconn, msgdata )
#             elif msgtype == '':
#                 msgtype = 'SRRY'
#                 msgdata = 'msgtype has not been provided by %s' % str(peerconn)
#                 self.handlers[ msgtype ]( peerconn, msgdata )
#             else:
#                 self.debug( Fore.BLUE + 'Handling peer msg: %s' % msgtype + '' + Fore.WHITE)
#                 self.handlers[ msgtype ]( peerconn, msgdata )
#         except KeyboardInterrupt:
#             raise
#         except:
#             if self.debug:
#                 traceback.print_exc()
