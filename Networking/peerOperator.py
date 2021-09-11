import threading
import traceback
from peerconnection import PeerConnection
from colorama.ansi import Fore
from peer import Peer
from multiprocessing import Process
from pynput.keyboard import Listener


"""
TODO's
-peer verification |P|
-maxpeer control |P|
-connection rejection |p|
"""

def runpeer(peer: Peer, debug: bool):
    def listener(MP: Process):
        def actions( key):
            if str(key) == "Key.ctrl_l":
                print("Peer shutting down ...")
                MP.terminate()
                return False
            if str(key) == "'s'":
                if __name__ == '__main__':
                    p = Process(target=peer.recCommand)
                    p.start()
        def runListener():  
            # Collect all event until released
            print("Keyboard listener initating...")
            print("    press ctrl to shut the program down")
            listener = Listener(on_press = actions)
            listener.start()
        runListener()
    if __name__ == '__main__':
        MP = Process(target=peer.mainloop, args=(debug,))
        MP.start()
        listener(MP=MP)
if __name__ == '__main__':
    local = input("local[y/n]:")
    if local == 'y':
        local = True
    else:
        local = False
    peer = Peer(True, 5512, local=local)
    runpeer(peer, True)