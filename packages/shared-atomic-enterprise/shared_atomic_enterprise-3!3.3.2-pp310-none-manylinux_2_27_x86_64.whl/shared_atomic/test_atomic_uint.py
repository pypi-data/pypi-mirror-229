import os

from shared_atomic.atomic_uint import atomic_uint
from shared_atomic.atomic_object import uint_get
from shared_atomic.atomic_object import uint_set
from shared_atomic.atomic_object import uint_get_and_set
from shared_atomic.atomic_object import uint_store
from shared_atomic.atomic_object import uint_shift
from shared_atomic.atomic_object import uint_compare_and_set
from shared_atomic.atomic_object import uint_compare_and_set_value
from shared_atomic.atomic_object import uint_add_and_fetch
from shared_atomic.atomic_object import uint_sub_and_fetch
from shared_atomic.atomic_object import uint_and_and_fetch
from shared_atomic.atomic_object import uint_or_and_fetch
from shared_atomic.atomic_object import uint_xor_and_fetch
from shared_atomic.atomic_object import uint_nand_and_fetch

from shared_atomic.atomic_object import uint_fetch_and_add
from shared_atomic.atomic_object import uint_fetch_and_sub
from shared_atomic.atomic_object import uint_fetch_and_and
from shared_atomic.atomic_object import uint_fetch_and_or
from shared_atomic.atomic_object import uint_fetch_and_xor
from shared_atomic.atomic_object import uint_fetch_and_nand

from threading import Thread
import sys, multiprocessing
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
    # atomic = ctypes.LibraryLoader(dlltype).LoadLibrary(filename)


def teardown_function():
    pass


def test_init():
    a = atomic_uint(2 ** 64 - 1)
    assert a.get() == 2 ** 64 - 1
    a = atomic_uint(0)
    assert a.get() == 0

def test_uint():
    for mode in ('m','s'):
        a = atomic_uint(2 ** 64 - 1, mode=mode)
        assert a.get() == 2 ** 64 - 1
        result = a.uint_get_and_set(2 ** 63 - 1)
        assert result == 2 ** 64 - 1
        assert a.get() == 2 ** 63 - 1
        result = a.uint_compare_and_set_value(2 ** 63 - 3, 2 ** 63 - 2)
        assert result == 2 ** 63 - 1
        assert a.get() == 2 ** 63 - 1
        result = a.uint_compare_and_set_value(2 ** 63 - 3, 2 ** 63 - 1)
        assert result == 2 ** 63 - 1
        assert a.get() == 2 ** 63 - 3

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_add_and_fetch((2 ** 62) - 1)
        assert result == 2 ** 64 - 1 + 2 ** 62 - 1 - 2 ** 64
        assert a.get() == 2 ** 64 - 1 + 2 ** 62 - 1 - 2 ** 64

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_sub_and_fetch(2 ** 62)
        assert result == 2 ** 64 - 1 - 2 ** 62
        assert a.get() == 2 ** 64 - 1 - 2 ** 62

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_and_and_fetch(2 ** 62)
        assert result == (2 ** 64 - 1) & (2 ** 62)
        assert a.get() == (2 ** 64 - 1) & (2 ** 62)

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_or_and_fetch(2 ** 62)
        assert result == (2 ** 64 - 1) | (2 ** 62)
        assert a.get() == (2 ** 64 - 1) | (2 ** 62)

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_xor_and_fetch(2 ** 62)
        assert result == (2 ** 64 - 1) ^ (2 ** 62)
        assert a.get() == (2 ** 64 - 1) ^ (2 ** 62)

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_nand_and_fetch(2 ** 62)
        assert result == 2**64 + (~((2 ** 64 - 1) & (2 ** 62)))
        assert a.get() == 2**64 + (~((2 ** 64 - 1) & (2 ** 62)))

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_fetch_and_add((2 ** 62) - 1)
        assert result == 2 ** 64 - 1
        assert a.get() == 2 ** 64 - 1 + (2 ** 62) - 1 - 2**64

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_fetch_and_sub(2 ** 62)
        assert result == 2 ** 64 - 1
        assert a.get() == 2 ** 64 - 1 - 2 ** 62

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_fetch_and_and(2 ** 62)
        assert result == 2 ** 64 - 1
        assert a.get() == (2 ** 64 - 1) & (2 ** 62)

        a = atomic_uint(0, mode=mode)
        result = a.uint_fetch_and_or(2 ** 62 - 1)
        assert result == 0
        assert a.get() == 0 | (2 ** 62 - 1)

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_fetch_and_xor(2 ** 62)
        assert result == 2 ** 64 - 1
        assert a.get() == (2 ** 64 - 1) ^ (2 ** 62)

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        result = a.uint_fetch_and_nand(2 ** 62)
        assert result == 2 ** 64 - 1
        assert a.get() == 2**64 + (~((2 ** 64 - 1) & (2 ** 62)))

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        b = atomic_uint(2 ** 63 - 2, mode=mode)
        result = a.uint_compare_and_set(b, 1)
        assert result == False
        assert a.get() == 2 ** 64 - 1
        assert b.get() == 2 ** 64 - 1

        result = a.uint_compare_and_set(b, 1)
        assert result == True
        assert a.get() == 1
        assert b.get() == 2 ** 64 - 1

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        b = atomic_uint(2 ** 63 - 2, mode=mode)
        a.uint_store(b)
        assert a.value == b.value
        assert b.value == 2 ** 63 - 2

        c = atomic_uint(2 ** 63 - 4)
        b = atomic_uint(2 ** 63 - 5)
        a.uint_shift(b, c)
        assert a.value == 2 ** 63 - 5
        assert b.value == 2 ** 63 - 5
        assert c.value == 2 ** 63 - 2

        a = atomic_uint(2 ** 64 - 1, mode=mode)
        reference=a
        assert uint_get(reference) == 2 ** 64 - 1
        uint_set(reference, 2 ** 63)
        assert uint_get(reference) == 2 ** 63
        assert uint_get_and_set(reference, 2 ** 63 - 1) == 2 ** 63
        assert uint_get(reference) == 2 ** 63 - 1
        assert uint_compare_and_set_value(reference, 2 ** 63 - 1, 2 ** 63 + 1) == 2 ** 63 - 1
        assert uint_get(reference) == 2 ** 63 - 1
        assert uint_compare_and_set_value(reference, 2 ** 63 + 1, 2 ** 63 - 1) == 2 ** 63 - 1
        assert uint_get(reference) == 2 ** 63 + 1

        uint_set(reference, 2 ** 64-1)
        assert uint_add_and_fetch(reference, 2 ** 63 - 1) == 2 ** 64 - 1 + 2 ** 63 - 1 - 2**64
        assert uint_get(reference) == 2 ** 64 - 1 + 2 ** 63 - 1 - 2**64

        uint_set(reference, 2 ** 64-1)
        assert uint_sub_and_fetch(reference, 2 ** 63 - 1) == 2 ** 64-1 -(2 ** 63 -1)
        assert uint_get(reference) == 2 ** 64-1 -(2 ** 63 -1)

        uint_set(reference, 2 ** 64-1)
        assert uint_and_and_fetch(reference, 2 ** 63 - 1) == (2 ** 64-1) & (2 ** 63 - 1)
        assert uint_get(reference) == (2 ** 64-1) & (2 ** 63 - 1)

        uint_set(reference, 0)
        assert uint_or_and_fetch(reference, 2 ** 63 - 1) == (0) | (2 ** 63 - 1)
        assert uint_get(reference) == 0 | (2 ** 63 - 1)

        uint_set(reference, 2 ** 64-1)
        assert uint_xor_and_fetch(reference, 2 ** 63 - 1) == (2 ** 64-1) ^ (2 ** 63-1)
        assert uint_get(reference) == (2 ** 64-1) ^ (2 ** 63-1)

        uint_set(reference, 2 ** 64-1)
        assert uint_nand_and_fetch(reference, 2 ** 63 - 1) == 2**64 + (~((2 ** 64-1) & (2 ** 63 - 1)))
        assert uint_get(reference) == 2**64 + (~((2 ** 64-1) & (2 ** 63 - 1)))

        uint_set(reference, 2 ** 64-1)
        assert uint_fetch_and_add(reference, 2 ** 63 - 1) == 2 ** 64-1
        assert uint_get(reference) == 2 ** 64-1 + 2 ** 63 - 1 - 2**64

        uint_set(reference, 2 ** 64-1)
        assert uint_fetch_and_sub(reference, 2 ** 63 - 1) == 2 ** 64-1
        assert uint_get(reference) == 2 ** 64-1 - (2 ** 63 - 1)

        uint_set(reference, 2 ** 64-1)
        assert uint_fetch_and_and(reference, 2 ** 63 - 1) == 2 ** 64-1
        assert uint_get(reference) == (2 ** 64-1) & (2 ** 63 - 1)

        uint_set(reference, 0)
        assert uint_fetch_and_or(reference, 2 ** 63 - 1) == 0
        assert uint_get(reference) == 0 | (2 ** 63 - 1)

        uint_set(reference, 2 ** 64-1)
        assert uint_fetch_and_xor(reference, 2 ** 63 - 1) == 2 ** 64-1
        assert uint_get(reference) == ((2 ** 64-1) ^ (2 ** 63 - 1))

        uint_set(reference, 2 ** 64-1)
        result = uint_fetch_and_nand(reference, 2 ** 63)
        assert result == 2 ** 64-1
        assert uint_get(reference) == 2**64 + (~((2 ** 64-1) & (2 ** 63)))

        uint_set(reference, 2 ** 64-1)
        uint_set(b, 2 ** 63)

        result = uint_compare_and_set(reference, b, 1)
        assert result == False
        assert uint_get(b)==  2 ** 64-1
        assert uint_get(reference)==  2 ** 64-1

        result = uint_compare_and_set(reference, b, 1)

        assert result == True
        assert uint_get(b)==  2 ** 64-1
        assert uint_get(reference)==  1

        b = atomic_uint(2 ** 63 - 2, mode=mode)
        uint_store(a, b)
        assert a.value == b.value

        c = atomic_uint(2 ** 63 - 4)
        b = atomic_uint(2 ** 63 - 5)
        uint_shift(a, b, c)
        assert a.value == 2 ** 63 - 5
        assert c.value == 2 ** 63 - 2

def thread_run(i):
    i.uint_add_and_fetch(100)


def test_thread_atomic():
    """
    test single process multiple threads
    :return: None
    """
    a = atomic_uint(0)

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
        a.uint_add_and_fetch(100)

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
    a = atomic_uint(0, mode='m', windows_unix_compatibility=True)
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
        uint_add_and_fetch(reference, 100)

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
    a = atomic_uint(0, mode='m')
    processlist = []

    for i in range(10):
        processlist.append(Process(target=process_run, args=(a,)))

    for i in range(10):
        processlist[i].start()

    for i in range(10):
        processlist[i].join()

    assert a.value == 10 * 50000 * 100
