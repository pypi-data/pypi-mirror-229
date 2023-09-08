from pathlib import Path
import string
import pytest

from shared_atomic.atomic_string import atomic_string
from shared_atomic.atomic_object import string_get_string
from shared_atomic.atomic_object import string_set_string
from shared_atomic.atomic_object import string_get_and_set
from shared_atomic.atomic_object import string_compare_and_set_value
from shared_atomic.atomic_object import string_shift
from shared_atomic.atomic_object import string_store
from shared_atomic.atomic_object import string_compare_and_set
import sys
from threading import Thread
import multiprocessing
from multiprocessing import Process
if sys.platform != 'win32':
    Process = multiprocessing.get_context('fork').Process
import random

inlist = (
         'a',
         'é',
         '重',
         '重重',
)


exlist = ('b',
         'è',
         '启',
         '轻轻',
          )

random_str1 = ''
random_str2 = ''

b = 0

#logger=logging.getLogger()
#logger.setLevel(logging.INFO)
#logging.basicConfig(filename = Path.joinpath(Path(__file__).parent,'log_test_atomic_string.log'),
#                    filemode='w',
#                    format='%(levelname) %(funcName)s %(lineno)d %(message)s',
 #                   level=logging.INFO)

#handler2 = RotatingFileHandler(Path.joinpath(Path(__file__).parent, 'log_test_atomic_string.log'),maxBytes=18*1024**3, backupCount=5)
#handler2.setFormatter(logging.Formatter('%(name) %(asctime)s %(msecs)d %(levelname) %(process)d %(thread)d %(funcName)s %(lineno)d %(message)s'))

#logging.basicConfig()

logfile = None

def signed2unsigned(input, i):
    if input < 0:
        return int.to_bytes(input + 2**((i+1)*8),length=i+1, byteorder='big').lstrip(b'\0')
    return int.to_bytes(input,length=2**i, byteorder='big').lstrip(b'\0')

def mylogger(data: str):
    print(data, file=logfile, flush=True)

def setup_function():
    """
    pre function for pytest
    :return: None
    """
    global logfile
    logfile = open(Path.joinpath(Path(__file__).parent, 'log_test_atomic_string.log'), 'a', encoding='utf-8')

    global random_str1, random_str2
    while True:
        random_str1 = ''
        random_str2 = ''
        try:
            for i in range(2):
                random_bytes = random.randrange(0, 65536).to_bytes(length=2, byteorder='big')
                random_str1 += random_bytes.decode('utf-16-le')

                random_bytes = random.randrange(0, 65536).to_bytes(length=2, byteorder='big')
                random_str2 += random_bytes.decode('utf-16-le')
            break
        except UnicodeDecodeError:
            continue

    mylogger("random_str1:" + str(random_str1.encode('utf-16-le')))
    mylogger("random_str2:" + str(random_str2.encode('utf-16-le')))

def teardown_function():
    logfile.close()

def test_init():

    for windows_unix_compatibility in (True, False):
        mylogger("windows_unix_compatibility:" + str(windows_unix_compatibility))
        #testing initialization with no padding or triming
        for encoding in {"utf-16-be", "utf-8", "utf-16"}:
            mylogger("encoding:" + encoding)
            for mode in ('m','s'):
                mylogger("mode:" + mode)
                while True:
                    random_str = ''
                    random_characters = random.randrange(0, 8)
                    for i in range(random_characters):
                        while True:
                            try:
                                random_bytes = random.randrange(0,65536).to_bytes(length=2, byteorder='big')
                                random_str += random_bytes.decode('utf-16-le')
                                break
                            except UnicodeDecodeError:
                                continue
                    length  = len(random_str.encode(encoding))
                    if length <= 7:
                        mylogger("random_str:" + random_str)
                        mylogger("length:" + str(length))
                        break
                a = atomic_string(random_str, length=length, encoding=encoding,
                                  mode=mode, windows_unix_compatibility=windows_unix_compatibility)
                assert a.user_windows_unix_compatibility == True
                assert a.value == random_str
                assert a.user_windows_unix_compatibility == True
                a = atomic_string(random_str,encoding=encoding,
                                  mode=mode, windows_unix_compatibility=windows_unix_compatibility)
                assert a.value == random_str
                assert a.user_windows_unix_compatibility == True


        #testing initialization with padding
        padding = {"utf-16-be": (1, 2, 7),
                   "utf-16": (1, 2, 7)
                   }
        for encoding in padding:
            mylogger("encoding:" + encoding)
            for mode in ('m', 's'):
                mylogger("mode:" + mode)
                for paddingdirection in ('l', 'r'):
                    mylogger("paddingdirection:" + paddingdirection)
                    random_characters, random_padding_length, length = padding[encoding]
                    while True:
                        try:
                            random_str = ''
                            random_pdding = ''
                            for i in range(random_characters):
                                random_bytes = random.randrange(0, 65536).to_bytes(length=2, byteorder='big')
                                random_str += random_bytes.decode('utf-16-be')
                            for i in range(random_padding_length):
                                random_bytes = random.randrange(0, 65536).to_bytes(length=2, byteorder='big')
                                random_pdding += random_bytes.decode('utf-16-be')
                            mylogger("random_str:" + random_str)
                            mylogger("random_pdding:" + random_pdding)
                            break
                        except UnicodeDecodeError:
                            continue
                    a = atomic_string(random_str, length=length,
                                      encoding=encoding, mode=mode,
                                      paddingstr=random_pdding, paddingdirection=paddingdirection,
                                      windows_unix_compatibility=windows_unix_compatibility)
                    assert a.user_windows_unix_compatibility == True
                    if paddingdirection == 'l':
                        assert a.value == (((random_pdding + random_str)[::-1]).encode(encoding)[:length]
                                           .decode(encoding, errors='ignore'))[::-1]
                    else:
                        assert a.value == ((random_str + random_pdding).encode(encoding)[:length]
                                           .decode(encoding, errors='ignore'))

        for mode in ('m', 's'):
            mylogger("mode:" + mode)
            for paddingdirection in ('l', 'r'):
                mylogger("paddingdirection:" + paddingdirection)
                random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                random_pdding = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
                mylogger("random_str:" + random_str)
                mylogger("random_pdding:" + random_pdding)
                a = atomic_string(random_str, length=7,
                                  encoding='utf-8', mode=mode,
                                  paddingstr=random_pdding, paddingdirection=paddingdirection,
                                  windows_unix_compatibility=windows_unix_compatibility)
                assert a.user_windows_unix_compatibility == True
                if paddingdirection == 'l':
                    assert a.value == (random_pdding * 2 + random_str)[-7:]
                else:
                    assert a.value == (random_str + random_pdding * 2)[:7]

        #testing initialization with trimming
        trimming = {"utf-16-be": (3, 5),
                   "utf-16": (4,5),
                    "utf-8": (10,7)
                   }
        for encoding in trimming:
            mylogger("encoding:" + encoding)
            random_characters, length = trimming[encoding]
            for mode in ('m', 's'):
                mylogger("mode:" + mode)
                for trimingdirection in ('l', 'r'):
                    mylogger("trimingdirection:" + trimingdirection)
                    while True:
                        try:
                            random_str = ''
                            for i in range(random_characters):
                                random_bytes = random.randrange(0, 65536).to_bytes(length=2, byteorder='big')
                                random_str += random_bytes.decode('utf-16-be')
                            mylogger("random_str:" + random_str)
                            break
                        except UnicodeDecodeError:
                            continue
                    a = atomic_string(random_str, length=length,
                                      encoding=encoding, mode=mode,
                                      trimming_direction=trimingdirection,
                                      windows_unix_compatibility=windows_unix_compatibility)
                    assert a.user_windows_unix_compatibility == True
                    if trimingdirection == 'l':
                        assert a.value == (random_str[::-1].encode(encoding)[:length]
                                           .decode(encoding, errors='ignore'))[::-1]
                    else:
                        assert a.value == (random_str.encode(encoding)[:length]
                                           .decode(encoding, errors='ignore'))

        pytest.raises(ValueError, atomic_string, '99999999')
        pytest.raises(ValueError, atomic_string, '9999', length=9)

def test_resize():
    a = atomic_string('ab1234567', length=7, encoding='utf-8')
    assert a.encoding=='utf-8'
    assert a.user_windows_unix_compatibility == True

    a.resize(6)
    assert a.value == 'ab1234'
    assert a.encoding=='utf-8'
    assert a.user_windows_unix_compatibility == True
    a.resize(7)
    assert a.value == 'ab1234 '
    assert a.encoding=='utf-8'
    assert a.user_windows_unix_compatibility == True

    a = atomic_string('ab1234567', length=7, encoding='utf-16')
    a.resize(6)
    assert a.value == 'ab'
    assert a.encoding=='utf-16'
    assert a.user_windows_unix_compatibility == True
    a.resize(7)
    assert a.value == 'ab'
    assert a.encoding=='utf-16'
    assert a.user_windows_unix_compatibility == True

def test_value_string():
    """
    test single process single thread
    :return: None
    """

    for windows_unix_compatibility in (True, False):
        mylogger("windows_unix_compatibility:" + str(windows_unix_compatibility))
        for mode in ('m','s'):
            mylogger("mode:" + mode)
            for i in range(4):
                mylogger("i=" + f'{i}')
                mylogger("inlist[i]:" + f'{inlist[i]}')
                mylogger("exlist[i]:" + f'{exlist[i]}')
                result = []
                a = atomic_string(inlist[i], windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                assert a.get_string() == inlist[i]
                if i != 3:
                    a = atomic_string('a' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                else:
                    a = atomic_string('a' * 7, trimming_direction='r',windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                a.set_string(inlist[i])
                assert a.value == inlist[i]

                result.append(a.string_get_and_set(exlist[i]))
                assert result[-1] == inlist[i]
                assert a.get_string() == exlist[i]

                result.append(a.string_compare_and_set_value("a", inlist[i]))
                assert result[-1] == exlist[i]
                assert a.get_string() == exlist[i]

                result.append(a.string_compare_and_set_value(inlist[i], exlist[i]))
                assert result[-1] == exlist[i]
                assert a.get_string() == inlist[i]

                if i != 3:
                    b = atomic_string('b' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                else:
                    b = atomic_string('b' * 7, trimming_direction='r',windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                result.append(a.string_compare_and_set(b, exlist[i]))
                assert result[-1] == False
                assert b.get_string() == inlist[i]

                result.append(a.string_compare_and_set(b, exlist[i]))
                assert result[-1] == True
                assert a.get_string() == exlist[i]

                if i != 3:
                    b = atomic_string('b' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                else:
                    b = atomic_string('b' * 7, trimming_direction='r',windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                value_b = b.get_string()
                a.string_store(b)
                assert a.get_string() == value_b
                assert b.get_string() == value_b

                if i != 3:
                    a = atomic_string('a' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                    b = atomic_string('b' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                    c = atomic_string('c' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                else:
                    a = atomic_string('a' * 7, trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                    b = atomic_string('b' * 7, trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                    c = atomic_string('c' * 7, trimming_direction='r',windows_unix_compatibility=windows_unix_compatibility, mode=mode)

                value_a = a.get_string()
                value_b = b.get_string()
                value_c = c.get_string()

                a.string_shift(b, c)
                assert a.get_string() == value_b
                assert c.get_string() == value_a
                assert b.get_string() == value_b

                a = atomic_string(inlist[i], windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                value = a.get_string()
                a.reencode('utf-16-le')
                assert a.value == value

                value = a.get_string()
                original_mode = a.mode
                pytest.raises(ValueError, a.change_mode, mode, windows_unix_compatibility=windows_unix_compatibility)
                assert original_mode == a.mode
                assert value == a.get_string()

                result = []
                a = atomic_string(inlist[i], windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                assert string_get_string(a) == inlist[i]
                string_set_string(a, inlist[i])
                assert a.value == inlist[i]

                result.append(string_get_and_set(a, exlist[i]))
                assert result[-1] == inlist[i]
                assert string_get_string(a) == exlist[i]
                c = []
                result.append(string_compare_and_set_value(a, "a", inlist[i]))
                assert result[-1] == exlist[i]
                assert string_get_string(a) == exlist[i]

                result.append(string_compare_and_set_value(a, inlist[i], exlist[i]))
                assert result[-1] == exlist[i]
                assert string_get_string(a) == inlist[i]

                b=atomic_string(exlist[i], mode=mode)
                result.append(string_compare_and_set(a, b, exlist[i]))
                assert result[-1] == False
                assert b.get_string() == inlist[i]

                result.append(string_compare_and_set(a, b, exlist[i]))
                assert result[-1] == True
                assert a.get_string() == exlist[i]

                if i != 3:
                    a = atomic_string('a' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                    b = atomic_string('b' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                    c = atomic_string('c' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                else:
                    a = atomic_string('a' * 7, trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                    b = atomic_string('b' * 7, trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                    c = atomic_string('c' * 7, trimming_direction='r',windows_unix_compatibility=windows_unix_compatibility, mode=mode)

                value_a = a.get_string()
                value_b = b.get_string()
                value_c = c.get_string()
                string_shift(a, b, c)
                assert a.get_string() == value_b
                assert b.get_string() == value_b
                assert c.get_string() == value_a

                if i != 3:
                    a = atomic_string('a' * (2 ** i), trimming_direction='r', windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                else:
                    a = atomic_string('a' * 7, trimming_direction='r',windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                value_a = a.get_string()
                result.append(string_compare_and_set(a, b, exlist[i]))
                assert result[-1] == False
                assert b.get_string() == value_a

                if i != 3:
                    b = atomic_string('b' * (2 ** i), trimming_direction='r',
                                      windows_unix_compatibility=windows_unix_compatibility, mode=mode)
                else:
                    b = atomic_string('b' * 7, trimming_direction='r',
                                      windows_unix_compatibility=windows_unix_compatibility, mode=mode)

                string_store(a, b)
                result.append(string_compare_and_set(a, b, exlist[i]))
                assert result[-1] == True
                assert a.get_string() == exlist[i]

                value = a.get_string()
                a.reencode('utf-16-le')
                assert a.value == value

                value = a.get_string()
                original_mode = a.mode
                pytest.raises(ValueError, a.change_mode, mode,
                              windows_unix_compatibility=windows_unix_compatibility)
                assert original_mode == a.mode
                assert value == a.get_string()

                if mode == 'm':
                    a.change_mode('s', windows_unix_compatibility=windows_unix_compatibility)
                    assert a.mode == 's'
                    assert a.value == value
                else:
                    a.change_mode('m', windows_unix_compatibility=windows_unix_compatibility)
                    assert a.mode == 'm'
                    assert a.value == value




def thread_run(a, lock):
    global b
    if a.string_compare_and_set_value(random_str2,random_str1) == random_str1:
        lock.acquire()
        b += 1
        lock.release()

def test_thread_atomic():
    """
    test single process multiple threads
    :return: None
    """
    import threading
    a = atomic_string(random_str1, encoding='utf-16')
    lock = threading.RLock()

    threadlist=[]

    for i in range(10000):
        threadlist.append(Thread(target=thread_run, args=(a, lock)))

    for i in range(10000):
        threadlist[i].start()

    for i in range(10000):
        threadlist[i].join()

    assert a.value == random_str2
    assert b == 1

def process_run(a,c, lock, random_str1, random_str2):
    def subthread_run(a: atomic_string, c, lock):
        nonlocal random_str1, random_str2
        if a.string_compare_and_set_value(random_str2[:], random_str1[:]) == random_str1[:]:
            lock.acquire()
            c.value += 1
            lock.release()

    threadlist = []
    for t in range(5000):
        threadlist.append(Thread(target=subthread_run, args=(a, c, lock,)))

    for t in range(5000):
        threadlist[t].start()

    for t in range(5000):
        threadlist[t].join()

def test_process_atomic_compatible():
        """
        test multiple processes
        :return: None
        """
        global random_str1, random_str2
        a = atomic_string(random_str1, mode='m', windows_unix_compatibility=True)
        c = multiprocessing.Value('i', lock=False)
        random_str1_shared = multiprocessing.Array('u', random_str1, lock=False)
        random_str2_shared = multiprocessing.Array('u', random_str2, lock=False)
        lock=multiprocessing.RLock()
        processlist = []
        for i in range(2):
            processlist.append(Process(target=process_run, args=(a,c, lock,random_str1_shared,random_str2_shared )))

        for i in range(2):
            processlist[i].start()

        for i in range(2):
            processlist[i].join()

        assert a.value == random_str2
        assert c.value == 1

if sys.platform == 'win32':

    def process_run_incompatible(a,c, lock, random_str1, random_str2):

        def subthread_run(string, reference, c, lock):
            nonlocal random_str1, random_str2
            if string_compare_and_set_value(string, reference, random_str2[:], random_str1[:]) == random_str1[:]:
                lock.acquire()
                c.value += 1
                lock.release()

        reference_a = get_reference(a)
        threadlist = []
        for t in range(5000):
            threadlist.append(Thread(target=subthread_run, args=(a, reference_a, c, lock)))

        for t in range(5000):
            threadlist[t].start()

        for t in range(5000):
            threadlist[t].join()

        release_reference(reference_a)

    def test_process_atomic_incompatible():
        """
        test multiple processes
        :return: None
        """
        global random_str1, random_str2
        a = atomic_string(random_str1, mode='m', encoding='utf-16')
        c = multiprocessing.Value('i', lock=False)
        random_str1_shared = multiprocessing.Array('u', random_str1, lock=False)
        random_str2_shared = multiprocessing.Array('u', random_str2, lock=False)
        lock=multiprocessing.RLock()
        processlist = []

        for i in range(10):
            processlist.append(Process(target=process_run_incompatible, args=(a,c,lock, random_str1_shared, random_str2_shared)))

        for i in range(10):
            processlist[i].start()

        for i in range(10):
            processlist[i].join()

        assert a.get_string() == random_str2
        assert c.value == 1

