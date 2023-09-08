from pathlib import Path
from shared_atomic.atomic_object import array_get_int
from shared_atomic.atomic_object import array_get_bytes
from shared_atomic.atomic_object import array_set_bytes
from shared_atomic.atomic_object import array_get_and_set
from shared_atomic.atomic_object import array_compare_and_set
from shared_atomic.atomic_object import array_compare_and_set_value

from shared_atomic.atomic_object import array_add_and_fetch
from shared_atomic.atomic_object import array_sub_and_fetch
from shared_atomic.atomic_object import array_and_and_fetch
from shared_atomic.atomic_object import array_or_and_fetch
from shared_atomic.atomic_object import array_xor_and_fetch
from shared_atomic.atomic_object import array_nand_and_fetch

from shared_atomic.atomic_object import array_fetch_and_add
from shared_atomic.atomic_object import array_fetch_and_sub
from shared_atomic.atomic_object import array_fetch_and_and
from shared_atomic.atomic_object import array_fetch_and_or
from shared_atomic.atomic_object import array_fetch_and_xor
from shared_atomic.atomic_object import array_fetch_and_nand


from shared_atomic.atomic_bytearray import atomic_bytearray
import random
import sys
from threading import Thread
import multiprocessing
from multiprocessing import Process
if sys.platform != 'win32':
    Process = multiprocessing.get_context('fork').Process
import json


a = None

inlist = (
         int.to_bytes(1, length=1, byteorder='big'),
         int.to_bytes(2**8+1, length=2, byteorder='big'),
         int.to_bytes(2**24+1, length=4, byteorder='big'),
         int.to_bytes(2**56+1, length=8, byteorder='big'),
)

inintlist = (
         1,
         2 ** 8 + 1,
         2 ** 24 + 1,
         2 ** 56 + 1,
)

exlist = (int.to_bytes(255, length=1, byteorder='big'),
          int.to_bytes(2 ** 16 - 1, length=2, byteorder='big'),
          int.to_bytes(2 ** 32 - 1, length=4, byteorder='big'),
          int.to_bytes(2 ** 64 - 1, length=8, byteorder='big'),
          )

exintlist = (255,
          2 ** 16 - 1,
          2 ** 32 - 1,
          2 ** 64 - 1)

sublist=[]
subintlist=[]
andlist = []
orlist = []
xorlist = []
nandlist = []
andintlist = []
orintlist = []
xorintlist = []
nandintlist = []
addlist = []
addintlist = []

logfile = None
r = None



def signed2unsigned(input: int, i: int):
    if input < 0:
        return int.to_bytes(input,length=2**i, byteorder='big', signed=True)
    else:
        return int.to_bytes(input,length=2**i+1, byteorder='big', signed=True)[-2**i:]


def mylogger(data: str):
    print(data, file=logfile, flush=True)

def setup_function():
    """
    pre function for pytest
    :return: None
    """
    global a, logfile, r, addlist, addintlist
    a = atomic_bytearray(b'ab1234567', length=7)
    logfile = open(Path.joinpath(Path(__file__).parent, 'log_test_atomic_bytearray.log'), 'a', encoding='utf-8')
    r = random.Random()

    for i in range(4):
        subintlist.append(r.randrange(0, 2 ** (8 * (i + 1) - 1)))
        sublist.append(subintlist[i].to_bytes(length=2 ** i, byteorder='big'))
        andintlist.append(r.randrange(0, 2 ** (8 * (i + 1) - 1)))
        andlist.append(int.to_bytes(andintlist[i], length=2 ** i, byteorder='big'))
        orintlist.append(r.randrange(0, 2 ** (8 * (i + 1) - 1)))
        orlist.append(int.to_bytes(orintlist[i], length=2 ** i, byteorder='big'))
        xorintlist.append(r.randrange(0, 2 ** (8 * (i + 1) - 1)))
        xorlist.append(int.to_bytes(xorintlist[i], length=2 ** i, byteorder='big'))
        nandintlist.append(r.randrange(0, 2 ** (8 * (i + 1) - 1)))
        nandlist.append(int.to_bytes(nandintlist[i], length=2 ** i, byteorder='big'))

    addlist = sublist
    addintlist = subintlist


def teardown_function():
    logfile.close()

def test_init():
    a = atomic_bytearray(b'ab')
    assert a.get_bytes() == b'ab'
    a = atomic_bytearray(b'ab', length=7, paddingdirection='l', paddingbytes=b'012')
    assert a.get_bytes() == b'12012ab'
    a = atomic_bytearray(b'ab', length=7)
    assert a.get_bytes() == b'ab\0\0\0\0\0'
    a = atomic_bytearray(b'ab1234567', length=7, trimming_direction='l')
    assert a.get_bytes() == b'1234567'
    a = atomic_bytearray(b'ab1234567', length=7)
    assert a.get_bytes() == b'ab12345'


def test_resize():
    #a=atomic_bytearray()
    a.resize(8)
    assert a.get_bytes() == b'ab12345'
    a.resize(7, trimming_direction='l')
    assert a.get_bytes() == b'ab12345'
    a.resize(8, paddingbytes=b'a', paddingdirection='l')
    assert a.get_bytes() == b'ab12345'
    a.resize(7, trimming_direction='l')
    assert a.get_bytes() == b'ab12345'
    a.resize(8, paddingbytes=b'a', paddingdirection='r')
    assert a.get_bytes() == b'ab12345'
    a.resize(4, paddingbytes=b'a', paddingdirection='r')
    assert a.get_bytes() == b'ab1'

def lpad0( array: atomic_bytearray, length: int):
    content=array.get_bytes()
    return b'\0' * (length-len(content)) + content

def test_value_bytearray():
    """
    test single process single thread
    :return: None
    """
    i = 0
    result = None
    for mode in ('s','m'):
        for i in range(4):
            mylogger("i=" + f'{i}')
            mylogger("inlist[i]=" + f'{inlist[i]}')
            mylogger("exlist[i]=" + f'{exlist[i]}')
            mylogger("addlist[i]=" + f'{addlist[i]}')
            mylogger("sublist[i]=" + f'{sublist[i]}')
            mylogger("andlist[i]=" + f'{andlist[i]}')
            mylogger("orlist[i]=" + f'{orlist[i]}')
            mylogger("xorlist[i]=" + f'{xorlist[i]}')
            mylogger("nandlist[i]=" + f'{nandlist[i]}')
            a = atomic_bytearray(b'a' * (2 ** i), mode=mode)
            assert a.get_int() == int.from_bytes(a.get_bytes(False), byteorder='big')
            result = []
            b = atomic_bytearray(inlist[i], mode=mode)
            result.append(a.array_get_and_set(exlist[i], False))
            assert result[-1] == b'a' * (2 ** i)
            assert a.get_bytes(False) == exlist[i]

            result.append(a.array_compare_and_set_value(exlist[i], inlist[i]))
            assert result[-1] == exlist[i]
            assert a.get_bytes(False) == exlist[i]

            result.append(a.array_compare_and_set_value(inlist[i], exlist[i]))
            assert result[-1] == exlist[i]
            assert a.get_bytes(False) == inlist[i]

            a=atomic_bytearray(exlist[i], mode=mode)
            b=atomic_bytearray(inlist[i], mode=mode)
            result.append(a.array_compare_and_set(b, inlist[i]))
            assert result[-1] == False
            assert a.get_bytes(False) == exlist[i]
            assert b.get_bytes(False) == exlist[i]

            result.append(a.array_compare_and_set(b, inlist[i]))
            assert result[-1] == True
            assert a.get_bytes(False) == inlist[i]
            assert b.get_bytes(False)  == exlist[i]

            a.set_bytes(exlist[i])
            assert a.get_bytes(False) == exlist[i]

            result.append(a.array_sub_and_fetch(sublist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] - addintlist[i], i)
            assert a.get_bytes(False) == result[-1]
            result.append(a.array_add_and_fetch(addlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i], i)
            assert a.get_bytes(False) == result[-1]
            a = atomic_bytearray(exlist[i], mode=mode)

            result.append(a.array_and_and_fetch(andlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] & andintlist[i],i)
            assert a.get_bytes(False) == result[-1]
            a = atomic_bytearray(exlist[i], mode=mode)

            result.append(a.array_or_and_fetch(orlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] | orintlist[i],i)
            assert a.get_bytes(False) == result[-1]
            a = atomic_bytearray(exlist[i], mode=mode)

            result.append(a.array_xor_and_fetch(xorlist[i], False))
            assert result[-1] ==signed2unsigned(exintlist[i] ^ xorintlist[i],i)
            assert a.get_bytes(False) == result[-1]
            a = atomic_bytearray(exlist[i], mode=mode)

            result.append(a.array_nand_and_fetch(nandlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] ^ nandintlist[i],i)
            assert a.get_bytes(False) == result[-1]
            a = atomic_bytearray(exlist[i], mode=mode)

            result.append(a.array_fetch_and_sub(sublist[i], False))
            assert result[-1] == exlist[i]
            assert a.get_bytes(False) == signed2unsigned(exintlist[i] - subintlist[i],i)

            a = atomic_bytearray(exlist[i], mode=mode)
            result.append(a.array_fetch_and_add(addlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i],i)
            assert a.get_bytes(False) == signed2unsigned(exintlist[i] + addintlist[i],i)

            a = atomic_bytearray(exlist[i], mode=mode)
            result.append(a.array_fetch_and_and(andlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i], i)
            assert a.get_bytes(False)  == signed2unsigned(exintlist[i] & andintlist[i],i)

            a = atomic_bytearray(exlist[i], mode=mode)
            result.append(a.array_fetch_and_or(orlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i],i)
            assert a.get_bytes(False)  == signed2unsigned(exintlist[i] | orintlist[i],i)

            a = atomic_bytearray(exlist[i], mode=mode)
            result.append(a.array_fetch_and_xor(xorlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i],i)
            assert a.get_bytes(False)  == signed2unsigned(exintlist[i] ^ xorintlist[i],i)

            a = atomic_bytearray(exlist[i], mode=mode)
            result.append(a.array_fetch_and_nand(nandlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i],i)
            assert a.get_bytes(False)  == signed2unsigned(~(exintlist[i] & nandintlist[i]),i)

            value = a.get_bytes(False)
            if mode != 'm':
                a.change_mode('m')
                assert value == a.get_bytes(False)
                assert a.mode == 'm'
            if mode != 's':
                a.change_mode('s')
                assert value == a.get_bytes(False)
                assert a.mode == 's'

            i += 1


        for i in range(4):
            mylogger("i=" + f'{i}')
            mylogger("inlist[i]=" + f'{inlist[i]}')
            mylogger("exlist[i]=" + f'{exlist[i]}')
            mylogger("addlist[i]=" + f'{addlist[i]}')
            mylogger("sublist[i]=" + f'{sublist[i]}')
            mylogger("andlist[i]=" + f'{andlist[i]}')
            mylogger("orlist[i]=" + f'{orlist[i]}')
            mylogger("xorlist[i]=" + f'{xorlist[i]}')
            mylogger("nandlist[i]=" + f'{nandlist[i]}')
            a = atomic_bytearray(b'a' * (2 ** i), mode=mode)
            assert array_get_int(a) == int.from_bytes(a.get_bytes(False), byteorder='big')

            result = []
            b = atomic_bytearray(inlist[i], mode=mode)
            result.append(array_get_and_set(a, exlist[i], False))
            assert result[-1] == b'a' * (2 ** i)
            assert array_get_bytes(a, False) == exlist[i]

            result.append(array_compare_and_set_value(a, exlist[i], inlist[i], False))
            assert result[-1] == exlist[i]
            assert array_get_bytes(a, False) == exlist[i]

            result.append(array_compare_and_set_value(a, inlist[i], exlist[i], False))
            assert result[-1] == exlist[i]
            assert array_get_bytes(a, False) == inlist[i]

            array_set_bytes(a, exlist[i])
            assert array_get_bytes(a, False) == exlist[i]

            b=atomic_bytearray(inlist[i], mode=mode)
            result.append(array_compare_and_set(a, b, inlist[i]))
            assert result[-1] == False
            assert array_get_bytes(a, False) == exlist[i]
            assert array_get_bytes(b, False) == exlist[i]

            result.append(array_compare_and_set(a, b, inlist[i]))
            assert result[-1] == True
            assert array_get_bytes(a, False) == inlist[i]
            assert array_get_bytes(b, False) == exlist[i]

            array_set_bytes(a, exlist[i])
            result.append(array_sub_and_fetch(a, sublist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] - addintlist[i],i)
            assert array_get_bytes(a, False) == result[-1]

            array_set_bytes(a, exlist[i])
            result.append(array_add_and_fetch(a, addlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] + addintlist[i],i)
            assert array_get_bytes(a, False) == result[-1]

            array_set_bytes(a, exlist[i])
            result.append(array_and_and_fetch(a, andlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] & andintlist[i],i)
            assert array_get_bytes(a, False) == result[-1]

            array_set_bytes(a, exlist[i])
            result.append(array_or_and_fetch(a, orlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] | andintlist[i],i)
            assert array_get_bytes(a, False) == result[-1]

            array_set_bytes(a, exlist[i])
            result.append(array_xor_and_fetch(a, xorlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] ^ xorintlist[i],i)
            assert array_get_bytes(a, False) == result[-1]

            array_set_bytes(a, exlist[i])
            result.append(array_nand_and_fetch(a, nandlist[i], False))
            assert result[-1] == signed2unsigned(~(exintlist[i] & nandintlist[i]),i)
            assert array_get_bytes(a, False) == result[-1]


            a = atomic_bytearray(exlist[i], mode=mode)
            result.append(array_fetch_and_sub(a,sublist[i], False))
            assert result[-1] == exlist[i]
            assert array_get_bytes(a, False) == int.to_bytes(exintlist[i] - subintlist[i], length=2 ** i, byteorder='big')
            result.append(array_fetch_and_add(a, addlist[i], False))
            assert result[-1] == int.to_bytes(exintlist[i] - subintlist[i], length=2 ** i, byteorder='big')
            assert array_get_bytes(a, False) == exlist[i]
            result.append(array_fetch_and_and(a,andlist[i], False))
            assert result[-1] == exlist[i]
            assert array_get_bytes(a, False)  == signed2unsigned(exintlist[i] & andintlist[i], i)
            result.append(array_fetch_and_or(a,orlist[i], False))
            assert result[-1] == signed2unsigned(exintlist[i] & andintlist[i], i)
            assert array_get_bytes(a, False)  == signed2unsigned((exintlist[i] & andintlist[i]) | orintlist[i], i)
            result.append(array_fetch_and_xor(a,xorlist[i], False))
            assert result[-1] == signed2unsigned((exintlist[i] & andintlist[i]) | orintlist[i], i)
            assert array_get_bytes(a, False)  == signed2unsigned(((exintlist[i] & andintlist[i]) | orintlist[i]) ^ xorintlist[i], i)
            result.append(array_fetch_and_nand(a,nandlist[i], False))
            assert result[-1] == signed2unsigned(((exintlist[i] & andintlist[i]) | orintlist[i]) ^ xorintlist[i], i)
            assert array_get_bytes(a, False)  == signed2unsigned(
                                                                          ~((((exintlist[i] & andintlist[i]) | orintlist[i]) ^ xorintlist[i]) & nandintlist[i])
                                                                         ,i)

            i += 1

def thread_run(a):
    a.array_sub_and_fetch(b'\x0F')


def test_thread_atomic():
    """
    test single process multiple threads
    :return: None
    """
    a = atomic_bytearray(b'ab', length=7, paddingdirection='r', paddingbytes=b'012', mode='s')

    threadlist=[]

    for i in range(10000):
        threadlist.append(Thread(target=thread_run, args=(a,)))

    for i in range(10000):
        threadlist[i].start()

    for i in range(10000):
        threadlist[i].join()

    assert a.value == int.to_bytes(27411031864108609,length=8,byteorder='big')

def process_run_compatible(a):
    def subthread_run(a: atomic_bytearray):
        a.array_sub_and_fetch(b'\x0F')

    threadlist = []
    for t in range(5000):
        threadlist.append(Thread(target=subthread_run, args=(a,)))

    for t in range(5000):
        threadlist[t].start()

    for t in range(5000):
        threadlist[t].join()

def test_process_atomic_compatible():
        """
        test multiple processes
        :return: None
        """
        a = atomic_bytearray(b'ab', length=7, paddingdirection='r', paddingbytes=b'012', mode='m', windows_unix_compatibility=True)

        processlist = []
        for p in range(2):
            processlist.append(Process(target=process_run_compatible, args=(a,)))

        for p in range(2):
            processlist[p].start()

        for p in range(2):
            processlist[p].join()

        assert a.value == int.to_bytes(27411031864108609,length=8,byteorder='big')

def process_run(array):
        def subthread_run(array):
            array_sub_and_fetch(array, b'\x0F')
        threadlist = []
        for t in range(50000):
            threadlist.append(Thread(target=subthread_run, args=(array,)))

        for t in range(50000):
            threadlist[t].start()

        for t in range(50000):
            threadlist[t].join()

def test_process_atomic_incompatible():
        """
        test multiple processes
        :return: None
        """
        a = atomic_bytearray(b'ab', length=7, paddingdirection='r', paddingbytes=b'012', mode='m')
        processlist = []

        for i in range(10):
            processlist.append(Process(target=process_run, args=(a,)))

        for i in range(10):
            processlist[i].start()

        for i in range(10):
            processlist[i].join()


        assert a.get_bytes(False) == b'\x00ab00\xbf\xbfQ'
