from shared_atomic.atomic_list import atomic_list
from shared_atomic.atomic_int import atomic_int
from shared_atomic.atomic_object import int_add_and_fetch
from shared_atomic.atomic_object import list_compare_and_set_value
from shared_atomic.atomic_object import list_get_int
from shared_atomic.atomic_object import list_set_int
from shared_atomic.atomic_object import list_get_list
from shared_atomic.atomic_object import list_set_list
from shared_atomic.atomic_object import list_get_and_set
from shared_atomic.atomic_object import list_store
from shared_atomic.atomic_object import list_shift
from shared_atomic.atomic_object import list_compare_and_set
from threading import Thread
from multiprocessing import Process
from pathlib import Path
import sys, multiprocessing
if sys.platform != 'win32':
    Process = multiprocessing.get_context('fork').Process

logfile = None

def mylogger(data: str):
    print(data, file=logfile, flush=True)

inlist = (
         'a',
         'é',
         '重1',
         '重重',
)

exlist = ('b',
         'è',
         '启2',
         '轻轻',
          )

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
    global logfile
    logfile = open(Path.joinpath(Path(__file__).parent, 'log_test_atomic_list.log'), 'a', encoding='utf-8')

def teardown_function():
    logfile.close()

def test_init():
    a = atomic_list([1, 2, 2, 3])
    assert a.get_list() == [1,2,2,3]
    a = atomic_list((True, False,))
    assert a.get_list() == [True, False]
    a = atomic_list([b'ab',b'cd'])
    assert a.get_list() == [b'ab',b'cd']
    a = atomic_list(['ab','cd'])
    assert a.get_list() == ['ab','cd']
    a = atomic_list(['中','国',b'1'],encoding='utf-16-le')
    assert a.get_list() == ['中','国',b'1']

    a = atomic_list([1,'中',True,b'x12'], encoding='utf-16-le')
    assert a.get_list() == [1,'中',True,b'x12']


def test_list():
    for mode in ('m','s'):
        a = atomic_list([1, '中', True, b'x12'], encoding='utf-16-le', mode=mode)
        assert a.get_int() ==12045398761102913842
        assert a.get_list() == [1, '中', True, b'x12']
        a = atomic_list([1], encoding='utf-16-le', mode=mode)
        a.set_list([0, '国', True, b'x21'])
        assert a.get_list() == [0, '国', True, b'x21']

        a.set_int(12045398761102913842)
        assert a.get_list() == [1, '中', True, b'x12']
        a.set_list([0, '国', True, b'x21'])

        result = a.list_compare_and_set_value([1, 2, 3], [1, '国', True, b'x12'])

        assert result == [0, '国', True, b'x21']
        assert a.get_list() == [0, '国', True, b'x21']


        result = a.list_compare_and_set_value([1, 2, 3], [0, '国', True, b'x21'])

        assert result == [0, '国', True, b'x21']
        assert [1, 2, 3] == a.get_list()

        a.value = [0, '国', True, b'x2']
        assert result == [0, '国', True, b'x21']
        a.reencode('utf-8')
        assert result == [0, '国', True, b'x21']
        a.value = [0, '中', True, b'x2']
        assert a.get_list() == [0, '中', True, b'x2']

        result = a.list_get_and_set([0, 1, 2, 3])
        assert result == [0, '中', True, b'x2']
        assert a.value == [0, 1, 2, 3]

        b=atomic_list([0, '中', True, b'x2'], mode=mode)
        a.list_store(b)
        assert a.value == [0, '中', True, b'x2']

        a.value = [0, 1, 2, 3]
        b=atomic_list([0, '中', True, b'x2'], mode=mode)
        c=atomic_list([0, '国', True, b'x2'], mode=mode)
        a.list_shift(b, c)
        assert a.value == [0, '中', True, b'x2']
        assert b.value == [0, '中', True, b'x2']
        assert c.value == [0, 1, 2, 3]

        a.value = [0, '中', True, b'x2']
        b=atomic_list([0, '国', True, b'x2'])
        assert a.list_compare_and_set(b, [0, 1, 2, 3]) == False
        assert a.value == [0, '中', True, b'x2']
        assert b.value == [0, '中', True, b'x2']

        assert a.list_compare_and_set(b, [0, 1, 2, 3]) == True
        assert a.value == [0, 1, 2, 3]
        assert b.value == [0, '中', True, b'x2']



        a = atomic_list([1, '中', True, b'x12'], encoding='utf-16-le', mode=mode)
        assert list_get_int(a) == 12045398761102913842
        assert list_get_list(a) == [1, '中', True, b'x12']
        a = atomic_list([1], encoding='utf-16-le', mode=mode)
        list_set_list(a, [0, '国', True, b'x2'])
        assert list_get_list(a) == [0, '国', True, b'x2']

        list_set_int(a, 12045398761102913842)
        assert list_get_list(a) == [1, '中', True, b'x12']
        list_set_list(a, [0, '国', True, b'x2'])

        result = list_compare_and_set_value(a, [1, 2, 3], [1, '国', True, b'x1'])
        assert result == [0, '国', True, b'x2']
        assert list_get_list(a) == [0, '国', True, b'x2']

        result = list_compare_and_set_value(a, [1, 2, 3], [0, '国', True, b'x2'])
        assert result == [0, '国', True, b'x2']
        assert [1, 2, 3] == list_get_list(a)

        a.value = [0, '中', True, b'x2']
        result = list_get_and_set(a, [0, 1, 2, 3])
        assert result == [0, '中', True, b'x2']
        assert list_get_list(a) == [0, 1, 2, 3]

        b=atomic_list([0, '中', True, b'x2'], encoding='utf-16-le', mode=mode)
        list_store(a, b)
        assert a.value == [0, '中', True, b'x2']

        a.value = [0, 1, 2, 3]
        b=atomic_list([0, '中', True, b'x2'], encoding='utf-16-le', mode=mode)
        c=atomic_list([0, '国', True, b'x2'], encoding='utf-16-le', mode=mode)
        list_shift(a, b, c)
        assert a.value == [0, '中', True, b'x2']
        assert c.value == [0, 1, 2, 3]

        a.value = [0, '中', True, b'x2']
        b=atomic_list([0, '国', True, b'x2'], encoding='utf-16-le', mode=mode)
        assert list_compare_and_set(a, b, [0, 1, 2, 3]) == False
        assert a.value == [0, '中', True, b'x2']
        assert b.value == [0, '中', True, b'x2']

        assert list_compare_and_set(a, b, [0, 1, 2, 3]) == True
        assert a.value == [0, 1, 2, 3]

def thread_run(a,i):
    if a.list_compare_and_set_value(['cd'], ['ab']) == ['ab']:
        i.int_add_and_fetch(1)

def test_thread_atomic():
    """
    test single process multiple threads
    :return: None
    """
    a = atomic_list(['ab'])
    b = atomic_int(0)

    threadlist = []

    for i in range(10000):
        threadlist.append(Thread(target=thread_run, args=(a, b)))

    for i in range(10000):
        threadlist[i].start()

    for i in range(10000):
        threadlist[i].join()

    assert a.value == ['cd']
    assert b.value == 1


def process_run_compatible(a,c):
        def subthread_run(a: atomic_list, c: atomic_int):
            if a.list_compare_and_set_value(['cd'],['ab']) == ['ab']:
                c.int_add_and_fetch(1)

        threadlist = []
        for t in range(5000):
            threadlist.append(Thread(target=subthread_run, args=(a,c)))

        for t in range(5000):
            threadlist[t].start()

        for t in range(5000):
            threadlist[t].join()

def test_process_atomic_compatible():
        """
        test multiple processes
        :return: None
        """
        a = atomic_list({'ab'}, mode='m', windows_unix_compatibility=True)
        c = atomic_int(0, mode='m', windows_unix_compatibility=True)
        processlist = []
        for i in range(2):
            processlist.append(Process(target=process_run_compatible, args=(a,c)))

        for i in range(2):
            processlist[i].start()

        for i in range(2):
            processlist[i].join()

        assert a.value == ['cd']
        assert c.value == 1


def process_run_incompatible(a, c):
        def subthread_run(list, integer):
            if list_compare_and_set_value(list, ['cd'], ['ab']) == ['ab']:
                int_add_and_fetch(c, 1)

        threadlist = []
        for t in range(5000):
            threadlist.append(Thread(target=subthread_run, args=(a, c,)))
        for t in range(5000):
            threadlist[t].start()
        for t in range(5000):
            threadlist[t].join()


def test_process_atomic_incompatible():
        """
        test multiple processes
        :return: None
        """
        a = atomic_list(['ab'], mode='m')
        c = atomic_int(0, mode='m')
        processlist = []

        for i in range(10):
            processlist.append(Process(target=process_run_incompatible, args=(a,c,)))

        for i in range(10):
            processlist[i].start()

        for i in range(10):
            processlist[i].join()

        assert a.get_list() == ['cd']
        assert c.get() == 1

