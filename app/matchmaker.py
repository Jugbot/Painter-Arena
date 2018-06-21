import arenapool
from multiprocessing import Process,Queue,Pipe, Pool
from celery import Celery

class Matchmaker:

    def __init__(self):
        self._in, child_out = Pipe()
        self._out = Queue()
        subprocess = Process(target=arenapool.init, args=(child_out, self._out))
        subprocess.daemon = True
        subprocess.start()

    def queue(self, req, callback=None):
        self._out.put_nowait(req)