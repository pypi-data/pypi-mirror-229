import os

from shared_atomic.atomic_int import atomic_int
from shared_atomic.atomic_object import int_get
from shared_atomic.atomic_object import int_set
from shared_atomic.atomic_object import int_get_and_set
from shared_atomic.atomic_object import int_store
from shared_atomic.atomic_object import int_shift
from shared_atomic.atomic_object import int_compare_and_set
from shared_atomic.atomic_object import int_compare_and_set_value
from shared_atomic.atomic_object import int_add_and_fetch
from shared_atomic.atomic_object import int_sub_and_fetch
from shared_atomic.atomic_object import int_and_and_fetch
from shared_atomic.atomic_object import int_or_and_fetch
from shared_atomic.atomic_object import int_xor_and_fetch
from shared_atomic.atomic_object import int_nand_and_fetch

from shared_atomic.atomic_object import int_fetch_and_add
from shared_atomic.atomic_object import int_fetch_and_sub
from shared_atomic.atomic_object import int_fetch_and_and
from shared_atomic.atomic_object import int_fetch_and_or
from shared_atomic.atomic_object import int_fetch_and_xor
from shared_atomic.atomic_object import int_fetch_and_nand

from threading import Thread
from multiprocessing import Process
import sys, multiprocessing
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
    # atomic = ctypes.LibraryLoader(dlltype).LoadLibrary(filename)


def teardown_function():
    pass


def test_init():
    a = atomic_int(2 ** 63 - 1)
    assert a.get() == 2 ** 63 - 1
    a = atomic_int(-2 ** 63)
    assert a.get() == -2 ** 63


def test_int():
    for mode in ('m','s'):
        a = atomic_int(2 ** 63 - 1, mode=mode)
        assert a.get() == 2 ** 63 - 1
        a.set(-2 ** 63)
        assert a.get() == -2 ** 63
        result = a.int_get_and_set(2 ** 63 - 1)
        assert result == -2 ** 63
        assert a.get() == 2 ** 63 - 1
        result = a.int_compare_and_set_value(2 ** 63 - 3, 2 ** 63 - 2)
        assert result == 2 ** 63 - 1
        result = a.int_compare_and_set_value(2 ** 63 - 3, 2 ** 63 - 1)
        assert result == 2 ** 63 - 1
        assert a.get() == 2 ** 63 - 3
        a = atomic_int(-2 ** 62, mode=mode)
        result = a.int_add_and_fetch(2 * (2 ** 62) - 1)
        assert result == 2 ** 62 - 1
        assert a.get() == 2 ** 62 - 1
        result = a.int_sub_and_fetch(2 * (2 ** 62) - 1)
        assert result == - 2 ** 62
        assert a.get() == - 2 ** 62
        result = a.int_fetch_and_add(2 * (2 ** 62) - 1)
        assert result == - 2 ** 62
        assert a.get() == 2 ** 62 - 1
        result = a.int_fetch_and_sub(2 * (2 ** 62) - 1)
        assert result == 2 ** 62 - 1
        assert a.get() == - 2 ** 62
        a.set(- 2 ** 61)
        result = a.int_fetch_and_and(2 ** 62)
        assert result == - 2 ** 61
        assert a.get() == (- 2 ** 61) & (2 ** 62)
        result = a.int_fetch_and_or(2 ** 62 - 1)
        assert result == 4611686018427387904  # (- 2 ** 63) & (2 ** 63)
        assert a.get() == 4611686018427387904 | (2 ** 62 - 1)
        result = a.int_fetch_and_xor(2 ** 62)
        assert result == 4611686018427387904 | (2 ** 62 - 1)
        assert a.get() == ((4611686018427387904 | (2 ** 62 - 1))) ^ (2 ** 62)
        a=atomic_int(2 ** 62, mode=mode)
        result = a.int_fetch_and_nand(-2 ** 63)
        assert result == 2 ** 62
        assert a.get() == ~((2 ** 62) & (-2 ** 63))

        b = atomic_int(2 ** 63 - 2, mode=mode)
        result = a.int_compare_and_set(b, 1)
        assert result == False
        assert b.get() == a.get()
        result = a.int_compare_and_set(b, 1)

        assert result == True
        assert a.get() == 1

        b = atomic_int(2 ** 63 - 2, mode=mode)
        a.int_store(b)
        assert a.value == b.value

        c = atomic_int(2 ** 63 - 4)
        b = atomic_int(2 ** 63 - 5)
        a.int_shift(b, c)
        assert a.value == 2 ** 63 - 5
        assert c.value == 2 ** 63 - 2

        a = atomic_int(((4611686018427387904 | (2 ** 62 - 1))) ^ (2 ** 62), mode=mode)
        reference = a
        assert int_get(reference) == ((4611686018427387904 | (2 ** 62 - 1))) ^ (2 ** 62)
        int_set(reference, -2 ** 63)
        assert int_get(reference) == -2 ** 63
        assert int_get_and_set(reference, 2 ** 63 - 1) == -2 ** 63
        assert int_get(reference) == 2 ** 63 - 1
        assert int_compare_and_set_value(reference, 2 ** 63 - 2, -2 ** 63 + 1) == 2 ** 63 - 1
        assert int_get(reference) == 2 ** 63 - 1
        assert int_compare_and_set_value(reference, -2 ** 63, 2 ** 63 - 1) == 2 ** 63 - 1
        assert int_get(reference) == -2 ** 63

        assert int_add_and_fetch(reference, 2 ** 63 - 1) == - 1
        assert int_get(reference) == - 1
        assert int_sub_and_fetch(reference, 2 ** 63 - 1) == -2 ** 63
        assert int_get(reference) == -2 ** 63
        assert int_and_and_fetch(reference, 2 ** 63 - 1) == 0
        assert int_get(reference) == 0
        assert int_or_and_fetch(reference, 2 ** 63 - 1) == 2 ** 63 - 1
        assert int_get(reference) == 2 ** 63 - 1
        assert int_xor_and_fetch(reference, 2 ** 63 - 1) == 0
        assert int_get(reference) == 0
        assert int_nand_and_fetch(reference, 2 ** 63 - 1) == -1
        assert int_get(reference) == -1

        int_set(reference, -2 ** 63)
        assert int_fetch_and_add(reference, 2 ** 63 - 1) == -2 ** 63
        assert int_get(reference) == -1
        assert int_fetch_and_sub(reference, 2 ** 63 - 1) == -1
        assert int_get(reference) == -2 ** 63
        assert int_fetch_and_and(reference, 2 ** 63 - 1) == -2 ** 63
        assert int_get(reference) == 0
        assert int_fetch_and_or(reference, 2 ** 63 - 1) == 0
        assert int_get(reference) == 2 ** 63 - 1
        assert int_fetch_and_xor(reference, 2 ** 63 - 1) == 2 ** 63 - 1
        assert int_get(reference) == 0

        a = atomic_int(2 ** 62, mode=mode)
        reference=a
        result = int_fetch_and_nand(reference, -2 ** 63)
        assert result == 2 ** 62
        assert int_get(reference) == ~((2 ** 62) & (-2 ** 63))

        b = atomic_int(2 ** 63 - 2, mode=mode)
        result = int_compare_and_set(reference, b, 1)
        assert result == False
        assert int_get(b)== int_get(reference)
        result = int_compare_and_set(reference, b, 1)

        assert result == True
        assert a.get() == 1

        b = atomic_int(2 ** 63 - 2, mode=mode)
        int_store(a, b)
        assert a.value == b.value

        c = atomic_int(2 ** 63 - 4, mode=mode)
        b = atomic_int(2 ** 63 - 5, mode=mode)
        int_shift(a, b, c)
        assert a.value == 2 ** 63 - 5
        assert c.value == 2 ** 63 - 2

def thread_run(i):
    i.int_add_and_fetch(100)


def test_thread_atomic():
    """
    test single process multiple threads
    :return: None
    """
    a = atomic_int(0)

    threadlist = []

    for i in range(10000):
        threadlist.append(Thread(target=thread_run, args=(a,)))

    for i in range(10000):
        threadlist[i].start()

    for i in range(10000):
        threadlist[i].join()

    assert a.value == 100 * 10000


def process_run_compatibility(a):
    def subthread_run(a):
        a.int_add_and_fetch(100)

    threadlist = []
    for t in range(50000):
        threadlist.append(Thread(target=subthread_run, args=(a,)))
    for t in range(50000):
        threadlist[t].start()
    for t in range(50000):
        threadlist[t].join()


def test_process_atomic_compatibility():
    """
    test multiple processes
    :return: None
    """
    a = atomic_int(0, mode='m', windows_unix_compatibility=True)
    processlist = []
    for i in range(10):
        processlist.append(Process(target=process_run_compatibility, args=(a,)))
    for i in range(10):
        processlist[i].start()
    for i in range(10):
        processlist[i].join()
    assert a.get() == 100 * 10 * 50000


def process_run(a):
    def subthread_run(reference):
        int_add_and_fetch(reference, 100)

    threadlist = []
    for t in range(50000):
        threadlist.append(Thread(target=subthread_run, args=(a,)))

    for t in range(50000):
        threadlist[t].start()

    for t in range(50000):
        threadlist[t].join()

def test_process_atomic_incompatible():
    """
    test multiple processes
    :return: None
    """
    a = atomic_int(0, mode='m')
    processlist = []

    for i in range(10):
        processlist.append(Process(target=process_run, args=(a,)))

    for i in range(10):
        processlist[i].start()

    for i in range(10):
        processlist[i].join()

    assert a.value == 10 * 50000 * 100
