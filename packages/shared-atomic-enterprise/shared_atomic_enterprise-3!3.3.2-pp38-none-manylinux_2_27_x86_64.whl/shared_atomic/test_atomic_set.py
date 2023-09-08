from shared_atomic.atomic_set import atomic_set
from shared_atomic.atomic_int import atomic_int
from shared_atomic.atomic_object import int_add_and_fetch
from shared_atomic.atomic_object import set_get_int
from shared_atomic.atomic_object import set_set_int
from shared_atomic.atomic_object import set_get_set
from shared_atomic.atomic_object import set_set_set
from shared_atomic.atomic_object import set_get_and_set
from shared_atomic.atomic_object import set_compare_and_set_value
from shared_atomic.atomic_object import set_store
from shared_atomic.atomic_object import set_shift
from shared_atomic.atomic_object import set_compare_and_set


from threading import Thread
from multiprocessing import Process
import sys, multiprocessing
if sys.platform != 'win32':
    Process = multiprocessing.get_context('fork').Process

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


def signed2unsigned(input, i):
    if input < 0:
        return int.to_bytes(input + 2**((i+1)*8),length=i+1, byteorder='big').lstrip(b'\0')
    return int.to_bytes(input,length=2**i, byteorder='big').lstrip(b'\0')


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

def test_init():
    a = atomic_set({1, 2, 3})
    assert a.get_set() == {1,2,3}
    a = atomic_set((True, False,))
    assert a.get_set() == {True, False}
    a = atomic_set({b'ab',b'cd'})
    assert a.get_set() == {b'ab',b'cd'}
    a = atomic_set({'ab','cd'})
    assert a.get_set() == {'ab','cd'}
    a = atomic_set({'中','国'},encoding='utf-16-le')
    assert a.get_set() == {'中','国'}

    a = atomic_set({1,'中',True,b'x12'}, encoding='utf-16-le')
    assert a.get_set() == {1,'中',True,b'x12'}

def test_set():
    for mode in ('m','s'):
        a = atomic_set({1, '中', True, b'x12'}, encoding='utf-16-le', mode=mode)
        assert a.get_set() == {1, '中', True, b'x12'}
        assert a.get_int() in (752924866570105138, 755418880573320526, 912520273452347698, 917507658187039333, 1074610920873078094, 1077104613244820125)
        a = atomic_set({1}, encoding='utf-16-le', mode=mode)
        a.set_set({0, '国', True, b'x21'})
        assert a.get_set() == {0, '国', True, b'x21'}
        a.set_int(752924866570105138)
        assert a.get_set() == {1, '中', True, b'x12'}
        a.set_set({0, '国', True, b'x21'})

        result = a.set_compare_and_set_value({1, 2, 3}, {0, '国', True, b'x12'})
        assert a.get_set() == {0, '国', True, b'x21'}
        assert result == {0, '国', True, b'x21'}

        result = a.set_compare_and_set_value({1, 2, 3}, {0, '国', True, b'x21'})
        assert result == {0, '国', True, b'x21'}
        assert a.get_set() == {1, 2, 3}

        a.set_set({0, '国', True, b'x2'})
        a.reencode('utf-8')
        assert a.value == {0, '国', True, b'x2'}
        a.reencode('utf-16-le')

        a.value = {0, '国', True, b'x24'}
        assert a.value == {0, '国', True, b'x24'}
        result = a.set_get_and_set({0, 1, 2, 3})
        assert result == {0, '国', True, b'x24'}
        assert a.value == {0, 1, 2, 3}

        b=atomic_set({0, '中', True, b'x2'}, mode=mode, encoding='utf-16-le')
        a.set_store(b)
        assert a.value == {0, '中', True, b'x2'}

        a.value = {0, 1, 2, 3}
        b=atomic_set({0, '中', True, b'x2'}, mode=mode, encoding='utf-16-le')
        c=atomic_set({0, '国', True, b'x21'}, mode=mode, encoding='utf-16-le')
        a.set_shift(b, c)
        assert a.value == {0, '中', True, b'x2'}
        assert b.value == {0, '中', True, b'x2'}
        assert c.value == {0, 1, 2, 3}

        a.set_set({0, '国', True, b'x21'})
        b=atomic_set({0, '国', True, b'x12'}, mode=mode, encoding='utf-16-le')
        assert a.set_compare_and_set(b, {1, 2, 3}) == False
        assert a.get_set() == {0, '国', True, b'x21'}

        assert a.set_compare_and_set(b, {0, '国', True, b'x12'}) == True
        assert b.get_set() == {0, '国', True, b'x21'}
        assert a.get_set() == {0, '国', True, b'x12'}


        a = atomic_set({1, '中', True, b'x12'}, encoding='utf-16-le', mode=mode)
        assert set_get_set(a) == {1, '中', True, b'x12'}
        assert set_get_int(a)  in (752924866570105138, 755418880573320526, 912520273452347698, 917507658187039333, 1074610920873078094, 1077104613244820125)


        set_set_set(a, {0, '国', True, b'x21'})
        assert set_get_set(a) == {0, '国', True, b'x21'}
        set_set_int(a, 752924866570105138)
        assert a.get_set() == {1, '中', True, b'x12'}
        set_set_set(a, {0, '国', True, b'x21'})

        result = set_compare_and_set_value(a, {1, 2, 3}, {0, '国', True, b'x12'})
        assert set_get_set(a) == {0, '国', True, b'x21'}
        assert result == {0, '国', True, b'x21'}

        result = a.set_compare_and_set_value({1, 2, 3}, {0, '国', True, b'x21'})
        assert result == {0, '国', True, b'x21'}
        assert set_get_set(a) == {1, 2, 3}

        a.value = {0, '国', True, b'x24'}
        result = set_get_and_set(a, {0, 1, 2, 3})
        assert result == {0, '国', True, b'x24'}
        assert a.value == {0, 1, 2, 3}

        b=atomic_set({0, '中', True, b'x2'}, encoding='utf-16-le', mode=mode)
        set_store(a, b)
        assert a.value == {0, '中', True, b'x2'}

        a.value = {0, 1, 2, 3}
        b=atomic_set({0, '中', True, b'x2'},encoding='utf-16-le', mode=mode)
        c=atomic_set({0, '国', True, b'x21'},encoding='utf-16-le', mode=mode)
        set_shift(a, b, c)
        assert a.value == {0, '中', True, b'x2'}
        assert b.value == {0, '中', True, b'x2'}
        assert c.value == {0, 1, 2, 3}

        a.set_set({0, '国', True, b'x21'})
        b=atomic_set({0, '国', True, b'x12'},encoding='utf-16-le', mode=mode)
        assert set_compare_and_set(a, b, {1, 2, 3}) == False
        assert set_get_set(a) == {0, '国', True, b'x21'}

        assert set_compare_and_set(a, b, {0, '国', True, b'x12'}) == True
        assert set_get_set(b) == {0, '国', True, b'x21'}
        assert set_get_set(a) == {0, '国', True, b'x12'}

def thread_run(a,i):
    if a.set_compare_and_set_value({'cd'}, {'ab'}) == {'ab'}:
        i.int_add_and_fetch(1)

def test_thread_atomic():
    """
    test single process multiple threads
    :return: None
    """
    a = atomic_set({'ab'})
    b = atomic_int(0)

    threadlist = []

    for i in range(10000):
        threadlist.append(Thread(target=thread_run, args=(a, b)))

    for i in range(10000):
        threadlist[i].start()

    for i in range(10000):
        threadlist[i].join()

    assert a.value == {'cd'}
    assert b.get() == 1


def process_run_compatible(a,c):
        def subthread_run(a: atomic_set, c: atomic_int):
            if a.set_compare_and_set_value({'cd'}, {'ab'}) == {'ab'}:
                c.int_add_and_fetch(1)

        threadlist = []
        for t in range(5000):
            threadlist.append(Thread(target=subthread_run, args=(a, c,)))

        for t in range(5000):
            threadlist[t].start()

        for t in range(5000):
            threadlist[t].join()

def test_process_atomic_compatible():
        """
        test multiple processes
        :return: None
        """
        a = atomic_set({'ab'}, mode='m', windows_unix_compatibility=True)
        c = atomic_int(0, mode='m', windows_unix_compatibility=True)
        processlist = []
        for i in range(2):
            processlist.append(Process(target=process_run_compatible, args=(a,c,)))

        for i in range(2):
            processlist[i].start()

        for i in range(2):
            processlist[i].join()

        assert a.get_set() == {'cd'}
        assert c.get() == 1

def process_run_incompatible(a, c):
    def subthread_run(a, c):
        if set_compare_and_set_value(a, {'cd'}, {'ab'}) == {'ab'}:
            int_add_and_fetch(c, 1)

    threadlist = []
    for t in range(5000):
        threadlist.append(Thread(target=subthread_run, args=(a,c,)))
    for t in range(5000):
        threadlist[t].start()
    for t in range(5000):
        threadlist[t].join()

def test_process_atomic_incompatible():
        """
        test multiple processes
        :return: None
        """
        a = atomic_set({'ab'}, mode='m')
        c = atomic_int(0, mode='m')
        processlist = []

        for i in range(10):
            processlist.append(Process(target=process_run_incompatible, args=(a,c,)))

        for i in range(10):
            processlist[i].start()

        for i in range(10):
            processlist[i].join()

        assert a.get_set() == {'cd'}
        assert c.get() == 1

