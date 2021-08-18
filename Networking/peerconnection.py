import socket
import traceback
import time

from colorama.ansi import Fore

class PeerConnection:
	def __init__( self, peerid, host, port, sock=None, debug=False ):
		if peerid:
			self.id = peerid
		else:
			self.id = (host, port)
		self.doDebug = debug

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
	def senddata(self, msgtype, msgdata):
		def makemsg(msgtype, msgdata):
			try:
				if msgtype and len(msgtype) == 4:
					msg = str(msgtype).upper()+":"+str(msgdata) 
					return msg
				else:
					return 'SRRY:Improper msgtype provided'
			except:
				addon = ''
				if self.doDebug: traceback.print_exc()
				else: addon += Fore.YELLOW +' set debug to True for details' + Fore.WHITE
				return 'SRRY:Faliure makingmsg'+addon
		try:
			msg = makemsg(msgtype, msgdata)
			l = str(len(msg)).encode()
			self.s.send(l)
			time.sleep(0.5)
			self.s.sendall(msg)
		except:
			addon = ''
			if self.doDebug: traceback.print_exc()
			else: addon += Fore.YELLOW +' set debug to True for details' + Fore.WHITE
			return 'SRRY:Failure sending data'+addon
	def recvdata(self):
		try:
			l = self.s.recv(1024).decode()
			msg = self.s.recv(int(l)).decode()
			return msg
		except:
			addon = ''
			if self.doDebug: traceback.print_exc()
			else: addon += Fore.YELLOW +' set debug to True for details'
			return 'SRRY:Failure reciving data'+addon