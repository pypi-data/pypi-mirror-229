from shared_atomic.atomic_boolfloat import atomic_bool, atomic_float
from shared_atomic.atomic_int import atomic_int
from shared_atomic.atomic_object import int_add_and_fetch
from shared_atomic.atomic_object import bool_get
from shared_atomic.atomic_object import bool_set
from shared_atomic.atomic_object import bool_store
from shared_atomic.atomic_object import bool_shift
from shared_atomic.atomic_object import bool_get_and_set
from shared_atomic.atomic_object import bool_compare_and_set
from shared_atomic.atomic_object import bool_compare_and_set_value
from shared_atomic.atomic_object import float_get
from shared_atomic.atomic_object import float_set
from shared_atomic.atomic_object import float_store

import sys
from threading import Thread
import multiprocessing
from multiprocessing import Process
if sys.platform != 'win32':
    Process = multiprocessing.get_context('fork').Process

def setup_function():
    """
    pre function for pytest
    :return: None
    """
    # if sys.platform in ('darwin','linux'):
    #     dlltype = ctypes.CDLL
    #     os.chdir('/Users/philren/.local/share/virtualenvs/spark-examples--HrH57AW/lib/python3.6/site-packages')
    #     filename = 'shared_atomic.cpython-36m-darwin.so'
    # elif sys.platform == "win32":
    #     dlltype = ctypes.windll
    # else:
    #     return
    #atomic = ctypes.LibraryLoader(dlltype).LoadLibrary(filename)

def teardown_function():
    pass

def test_bool():
    for mode in ('s','m'):
        a = atomic_bool(True, mode=mode)
        assert a.get() == True
        assert a.user_windows_unix_compatibility == True

        a = atomic_bool(False, mode=mode, windows_unix_compatibility=True)
        assert a.value == False
        assert a.user_windows_unix_compatibility == True

        a = atomic_bool(True, mode=mode, windows_unix_compatibility=False)
        assert a.value == True
        assert a.user_windows_unix_compatibility == True

        a = atomic_bool(True, mode=mode, windows_unix_compatibility=True)
        assert a.get() == True
        assert a.bool_get_and_set(False) == True
        assert a.get() == False
        a.set(True)
        assert a.get() == True
        assert a.bool_compare_and_set_value(False, False) == True
        assert a.get() == True
        assert a.bool_compare_and_set_value(False, True) == True
        assert a.value == False
        a.set(True)
        assert a.get() == True
        b=atomic_bool(False, mode=mode)
        a.bool_store(b)
        assert a.get() == False

        b=atomic_bool(True, mode=mode)
        assert a.bool_compare_and_set(b, True) == False
        assert a.get() == False
        assert b.get() == False

        assert a.bool_compare_and_set(b, True) == True
        assert a.get() == True
        assert b.get() == False

        b=atomic_bool(False, mode=mode)
        c=atomic_bool(True, mode=mode)

        a.bool_shift(b, c)
        assert c.value == True
        assert a.value == False
        assert b.value == False

        a=atomic_float(sys.float_info.max)
        assert a.value == sys.float_info.max
        a.value = sys.float_info.min
        assert a.value == sys.float_info.min
        b=atomic_float(sys.float_info.max)
        a.float_store(b)
        assert a.value == sys.float_info.max

        a = atomic_bool(True, mode=mode, windows_unix_compatibility=True)
        assert bool_get(a) == True
        bool_set(a, False)
        assert bool_get(a) == False
        assert bool_get_and_set(a, True) == False
        assert bool_get(a) == True
        assert bool_compare_and_set_value(a, False, False) == True
        assert bool_get(a) == True
        assert bool_compare_and_set_value(a, False, True) == True
        assert bool_get(a) == False

        bool_set(a, True)
        assert a.get() == True
        b=atomic_bool(False, mode=mode)
        bool_store(a, b)
        assert a.get() == False

        b=atomic_bool(True, mode=mode)
        assert bool_compare_and_set(a, b, True) == False
        assert bool_get(a) == False
        assert bool_get(b) == False

        assert bool_compare_and_set(a, b, True) == True
        assert bool_get(a) == True
        assert bool_get(b) == False

        b=atomic_bool(False, mode=mode)
        c=atomic_bool(True, mode=mode)

        bool_shift(a, b, c)
        assert c.value == True
        assert a.value == False
        assert b.value == False

        a=atomic_float(sys.float_info.max)
        assert float_get(a) == sys.float_info.max
        float_set(a, sys.float_info.min)
        assert float_get(a) == sys.float_info.min
        b=atomic_float(sys.float_info.max)
        float_store(a, b)
        assert float_get(a) == sys.float_info.max

def thread_run(a, c):
        if not a.bool_compare_and_set_value(True, False):
            c.int_add_and_fetch(1)

def test_thread_atomic():
        """
        test single process multiple threads
        :return: None
        """
        a = atomic_bool(False)
        c = atomic_int(0)
        threadlist = []
        for i in range(10000):
            threadlist.append(Thread(target=thread_run, args=(a,c)))
        for i in range(10000):
            threadlist[i].start()
        for i in range(10000):
            threadlist[i].join()
        assert a.value == True
        assert c.value == 1

def process_run_compatible(a, c):
    def subthread_run(a:atomic_bool, c: atomic_int):
        if not a.bool_compare_and_set_value(True, False) and a.get() == True:
            c.int_add_and_fetch(1)

    threadlist = []
    for t in range(5000):
        threadlist.append(Thread(target=subthread_run, args=(a, c)))

    for t in range(5000):
        threadlist[t].start()

    for t in range(5000):
        threadlist[t].join()


def test_process_atomic_compatible():
    """
    test multiple processes
    :return: None
    """
    a = atomic_bool(False, mode='m', windows_unix_compatibility=True)
    c = atomic_int(0, mode='m', windows_unix_compatibility=True)
    processlist = []
    for i in range(2):
        processlist.append(Process(target=process_run_compatible, args=(a, c)))

    for i in range(2):
        processlist[i].start()

    for i in range(2):
        processlist[i].join()

    assert c.value == 1
    assert a.value == True


def process_run(a, c):

        def subthread_run(reference_a, reference_c):
            if not bool_compare_and_set_value(reference_a, True, False):
                if bool_get(reference_a) == True:
                    int_add_and_fetch(reference_c, 1)

        threadlist = []
        for t in range(5000):
            threadlist.append(Thread(target=subthread_run, args=(a, c)))

        for t in range(5000):
            threadlist[t].start()

        for t in range(5000):
            threadlist[t].join()

def test_process_atomic_incompatible():
        """
        test multiple processes
        :return: None
        """
        a = atomic_bool(False, mode='m',windows_unix_compatibility=False)
        c = atomic_int(0, mode='m', windows_unix_compatibility=False)

        processlist = []

        for i in range(10):
            processlist.append(Process(target=process_run, args=(a,c,)))

        for i in range(10):
            processlist[i].start()

        for i in range(10):
            processlist[i].join()

        assert a.value == True
        assert c.value == 1
