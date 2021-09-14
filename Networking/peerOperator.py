from peer import Peer
from multiprocessing import Process
from pynput.keyboard import Listener
from awincheck import getForegroundWindowTitle


"""
TODO's
peer identity verification
"""

def runpeer(peer: Peer, debug: bool, win: str):
    def listener(MP: Process, win: str):
        def actions( key):
            if str(key) == "Key.ctrl_l" and getForegroundWindowTitle() == win:
                print("Peer shutting down ...")
                MP.terminate()
                return False
            if str(key) == "'s'" and getForegroundWindowTitle() == win:
                if __name__ == '__main__':
                    p = Process(target=peer.recCommand)
                    p.start()
        def runListener():  
            print("Keyboard listener initating...")
            print("    press ctrl to shut the program down")
            listener = Listener(on_press = actions)
            listener.start()
        runListener()
    if __name__ == '__main__':
        MP = Process(target=peer.mainloop, args=(debug,))
        MP.start()
        listener(MP=MP, win=win)
if __name__ == '__main__':
    local = input("local[y/n]: ")
    if local.upper() == 'Y' or local.upper() == 'YES':
        local = True
    else:
        local = False
    maxpeers = input("maxpeers: ")
    try:
        maxpeers = int(maxpeers)
    except:
        maxpeers = 15
    win = getForegroundWindowTitle()
    peer = Peer(True, 5512, local=local, maxpeers=maxpeers)
    runpeer(peer, True, win=win)