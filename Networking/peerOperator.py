from peer import Peer
from multiprocessing import Process
from pynput.keyboard import Listener

def runpeer(peer: Peer, debug: bool):
    def listener(MP: Process):
        def actions( key):
            if str(key) == "Key.ctrl_l":
                print("Peer shutting down ...")
                MP.terminate()
                return False
        def runListener():  
            # Collect all event until released
            print("Keyboard listener initating...")
            print("    press ctrl to shut the program down")
            with Listener(on_press = actions) as listener:
                listener.join()
        runListener()
    if __name__ == '__main__':
        MP = Process(target=peer.mainloop, args=(debug,))
        MP.start()
        listener(MP=MP)
    else:
        print(__name__)

    
peer = Peer(True, 5505, local=True)
runpeer(peer, True)