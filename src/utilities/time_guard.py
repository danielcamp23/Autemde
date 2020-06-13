import signal
from contextlib import contextmanager

@contextmanager
def time_guard(timeout):
	#Register the signal
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(timeout)

    try:
        yield
    except:
        pass
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
	    signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_IGN)