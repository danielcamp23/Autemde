import sys
import threading
import select

CTR_CHECK_THREAD_FINISH = 200
READ_TIMEOUT_S = 1

class IDScanner:
    def __init__(self, cb):
        self._cb = cb
        self.run = False
        self.finish_thread = False
        self.t = threading.Thread(target=self._reading_thread)
        self.lock = threading.Lock()

    def start(self):
        self.finish_thread = False

        if self.t.is_alive():
            return
        else:    
            self.t.start()

        print("started")


    def stop(self):
        self.lock.acquire()
        try:
            self.finish_thread = True
        finally:
            self.lock.release()

    def _reading_thread(self):
        lock_ctr = 0
        print("Finish Thread ****")
        while True:
            lock_ctr += 1
            if lock_ctr % CTR_CHECK_THREAD_FINISH == 0 and self._is_thread_to_be_finished() == True:
                print("Finish Thread")
                break

            #Only read Read Descriptors - no 23172791


            
            if sys.stdin in select.select([sys.stdin], [], [], READ_TIMEOUT_S)[0]:
                #Data available to be read
                self._cb(sys.stdin.readline())
            

        print("ID detector thread finished!")


    def _is_thread_to_be_finished(self):
        finish_thread = False
        acquired = self.lock.acquire(blocking=False, timeout=-1)
        try:
            if acquired:
                finish_thread = self.finish_thread
        finally:
            if acquired:
                self.lock.release()

        return finish_thread

