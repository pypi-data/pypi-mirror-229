import array
import tempfile

from shared_atomic.atomic_object import array2d
from shared_atomic.atomic_object import shared_memory_offset_get
from shared_atomic.atomic_object import shared_memory_offset_get_and_set
from shared_atomic.atomic_object import shared_memory_offset_store
from shared_atomic.atomic_object import shared_memory_offset_store_from_other_types
from shared_atomic.atomic_object import shared_memory_offset_compare_and_set
from shared_atomic.atomic_object import shared_memory_offset_compare_with_other_type_and_set
from shared_atomic.atomic_object import shared_memory_offset_compare_and_set_value


from shared_atomic.atomic_object import shared_memory_offset_add_and_fetch
from shared_atomic.atomic_object import shared_memory_offset_sub_and_fetch
from shared_atomic.atomic_object import shared_memory_offset_and_and_fetch
from shared_atomic.atomic_object import shared_memory_offset_or_and_fetch
from shared_atomic.atomic_object import shared_memory_offset_xor_and_fetch
from shared_atomic.atomic_object import shared_memory_offset_nand_and_fetch

from shared_atomic.atomic_object import shared_memory_offset_fetch_and_add
from shared_atomic.atomic_object import shared_memory_offset_fetch_and_sub
from shared_atomic.atomic_object import shared_memory_offset_fetch_and_and
from shared_atomic.atomic_object import shared_memory_offset_fetch_and_or
from shared_atomic.atomic_object import shared_memory_offset_fetch_and_xor
from shared_atomic.atomic_object import shared_memory_offset_fetch_and_nand



from shared_atomic.atomic_shared_memory import atomic_shared_memory
import pytest
import sys, multiprocessing
from threading import Thread
from multiprocessing import Process
if sys.platform != 'win32':
    Process = multiprocessing.get_context('fork').Process
import stat
import os
import multiprocessing
import random
import copy
from array import array

from shared_atomic.atomic_int import atomic_int

def  unsigned2signed(size, input) -> int:
        r"""
        transform of unsigned integer to signed integer,

        :param input: value to be change
        :return: the signed integer
        """
        if input < 2 ** (size * 8 - 1):
            return input
        else:
            return input - 2 ** (size * 8)

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
def teardown_function():
    pass

def test_init():
    a = atomic_shared_memory(length=1024**3)
    assert a.offset_get(length=1) == b'\0'
    a = atomic_shared_memory(b'1024', mode='m', paddingdirection='l', paddingbytes=b'cdef', length=1024**2)
    assert a.offset_get(offset=1024**2-4, length=4) == b'1024'
    mv = array('B', a.size * b'\0')
    a.offset_memmove(mv, 0, 'o')
    assert bytes(mv[:4]) == b'cdef'


    a = atomic_shared_memory(b'1024'*1024, mode='m',trimming_direction='l', length=1024*2-1)
    if sys.platform != 'win32':
        assert a.offset_get(offset=1024*2-5, length=4) == b'1024'
        a = atomic_shared_memory(b'1024'*1024, trimming_direction='r', length=1024*2+1)
        assert a.offset_get(offset=1024*2-7, length=8) == b'02410241'
        assert a.offset_get(offset=1024*2-7, length=2) == b'02'
        assert a.offset_get(offset=1024*2-6, length=1) == b'2'
    else:
        assert a.offset_get(offset=12, length=4) == b'0241'
        assert a.offset_get(offset=16, length=4) == b'0241'
        assert a.offset_get(offset=16, length=8) == b'02410241'
        assert a.offset_get(offset=1024*2-2, length=1) == b'4'


    with pytest.raises(OSError):
        a = atomic_shared_memory(source='f', previous_shared_memory_path='/Users/')
    a = atomic_shared_memory(initial=b'1024', mode='m', length=1024, source='p', standalone=True)
    mv = array('B', a.size * b'\0')
    a.offset_memmove(mv, 0, 'o')
    contents=bytes(mv[:])
    filename=a.f.name
    a = None
    a = atomic_shared_memory(previous_shared_memory_path=filename, length=1024, source='f')
    mv = array('B', a.size * b'\0')
    a.offset_memmove(mv, 0, 'o')
    assert bytes(mv[:]) == contents
    a = None
    a = atomic_shared_memory(previous_shared_memory_path=filename, length=1020, source='f', remove_previous_file=True)
    mv = array('B', a.size * b'\0')
    a.offset_memmove(mv, 0, 'o')
    assert bytes(mv[:]) == contents[:1020]
    with pytest.raises(FileNotFoundError):
        os.stat(filename)
    a = None
    a = atomic_shared_memory(initial=b'1024'*(1024*1024//4), mode='m', length=1024*1024-1, trimming_direction='l', source='p', standalone=True)
    a.file_sync()
    f=open(a.f.name,'rb')
    mv = array('B', a.size * b'\0')
    a.offset_memmove(mv, 0, 'o')
    assert bytes(mv[:4])==b'0241'
    mv = array('B', a.size * b'\0')
    a.offset_memmove(mv, 0, 'o')
    contents=bytes(mv[:])
    assert f.read()[::-1][:-1] == contents
    f.close()


    filename=a.f.name
    with pytest.raises(ValueError):
        a = atomic_shared_memory(source='f', standalone=True, remove_previous_file=False)
    a = None
    a = atomic_shared_memory(previous_shared_memory_path=filename, length=1024*1024*1024-1, source='f', remove_previous_file=True)
    fd, filename = tempfile.mkstemp()
    print(filename)
    os.close(fd)
    a.memdump(filename)
    f=open(filename,'rb')
    mv = array('B', a.size * b'\0')
    a.offset_memmove(mv, 0, 'o')
    contents=bytes(mv[:])
    assert f.read()[::-1][:-1] == contents
    f.close()
    os.unlink(filename)







def test_shared_memory():

    for length in (1,2,3,4,8):

        length_a=1024*2+1
        random_offset_a=random.randrange(0, length_a-length)
        print('random_offset_a='+f'{random_offset_a}')
        length_b=1024*2+1
        random_offset_b=random.randrange(0, length_b-length)
        print('random_offset_b='+f'{random_offset_b}')
        print('length='+f'{length}')



        a = atomic_shared_memory(b'1024'*1024, mode='m', trimming_direction='r', length=length_a)
        b = atomic_shared_memory(b'1024'*1024, trimming_direction='r', length=length_b)
        if length == 3:
            pytest.raises(ValueError, a.offset_store, b, random_offset_a, random_offset_b, length)
            pytest.raises(ValueError, a.offset_compare_and_set, b, b'abc', random_offset_a, random_offset_a)
            pytest.raises(ValueError, a.offset_compare_and_set_value, b'abc', b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_compare_and_set_value, b'abcd', b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_add_and_fetch, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_sub_and_fetch, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_and_and_fetch, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_or_and_fetch, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_xor_and_fetch, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_nand_and_fetch, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_nand_and_fetch, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_fetch_and_add, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_fetch_and_sub, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_fetch_and_and, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_fetch_and_or, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_fetch_and_xor, b'abd', random_offset_a)
            pytest.raises(ValueError, a.offset_fetch_and_nand, b'abd', random_offset_a)
        else:
            random_value1 = int.to_bytes(random.randint(0, 2**63), length=8, byteorder='big')[0:length]
            random_value2 = int.to_bytes(random.randint(0, 2**63), length=8, byteorder='big')[0:length]

            print('random_value1=' + f'{random_value1}')
            print('random_value2=' + f'{random_value2}')

            original_a=bytes(b.buf[:])
            result = a.offset_get(random_offset_a, length)
            assert bytes(a.buf[:]) == original_a
            assert result == bytes(original_a[random_offset_a:random_offset_a+length])

            original_a=bytes(b.buf[:])
            result = a.offset_get_and_set(random_value1, random_offset_a)
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+ random_value1 + original_a[random_offset_a+length:]
            assert result == bytes(original_a[random_offset_a:random_offset_a+length])

            r"""a=b'1024'
                b=b'1024'"""
            original_a=bytes(b.buf[:])
            original_b=bytes(b.buf[:])
            a.offset_store(b, random_offset_a, random_offset_b, length)
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+ bytes(original_b[random_offset_b:random_offset_b+length]) + original_a[random_offset_a+length:]
            assert bytes(b.buf[:]) == original_b


            random_offset_a2 = random.randrange(0, length_a - 8)
            b=atomic_int(int.from_bytes(random_value1, byteorder='big'), 's', False)
            original_a=bytes(a.buf[:])
            original_b=b.value
            original_b_size=b.size
            a.offset_store_from_other_types(b, random_offset_a2)
            assert bytes(a.buf[:]) == original_a[:random_offset_a2] + \
                   original_b.to_bytes(length=original_b_size, byteorder='big') + \
                   original_a[random_offset_a2+original_b_size:]
            assert b.value == original_b


            b = atomic_shared_memory(b'5678' * 1024, trimming_direction='r', length=length_b)
            original_a=bytes(a.buf[:])
            original_b=bytes(b.buf[:])
            result = a.offset_compare_and_set(b, random_value1, random_offset_a, random_offset_b)
            assert result == False
            assert bytes(a.buf[:]) == original_a
            assert bytes(b.buf[:]) == original_b[:random_offset_b]+bytes(original_a[random_offset_a:random_offset_a+length])+bytes(original_b[random_offset_b+length:])

            original_b=bytes(b.buf[:])
            result = a.offset_compare_and_set(b, random_value1, random_offset_a, random_offset_b)
            assert result == True
            assert bytes(a.buf[:]) == original_a[:random_offset_a] + random_value1 + original_a[random_offset_a+length:]
            assert bytes(b.buf[:]) == original_b


            '''
            b = atomic_int(2**(2**length-1))
            original_a=bytes(a.buf[:])
            original_b=int.to_bytes(b.value, length=length, byteorder='big', signed=True)
            result = a.offset_compare_with_other_type_and_set(b, random_value1, random_offset_a)
            assert result == (original_b == original_a[random_offset_a: random_offset_a + length])
            assert int.to_bytes(b.value, length=length, byteorder='big', signed=True) == original_a[random_offset_a: random_offset_a + length]
            if result == True:
                assert bytes(a.buf[:]) == original_a[:random_offset_a] + random_value1 + original_a[random_offset_a+length:]
            else:
                result = a.offset_compare_with_other_type_and_set(b, random_value1, random_offset_a)
                assert result == True
                assert bytes(a.buf[:]) == original_a[:random_offset_a] + random_value1 + original_a[random_offset_a+length:]
                assert int.to_bytes(b.value, length=length, byteorder='big', signed=True) == original_a[random_offset_a: random_offset_a+length]
            '''

            original_a=bytes(a.buf[:])
            original_a_offset_value = original_a[random_offset_a: random_offset_a+length]
            result = a.offset_compare_and_set_value(random_value1, random_value2, random_offset_a)
            assert result == original_a_offset_value
            assert bytes(a.buf[:]) == original_a

            result = a.offset_compare_and_set_value(random_value2, original_a_offset_value, random_offset_a)
            assert result == original_a_offset_value
            assert bytes(a.buf[:]) == bytes(original_a[:random_offset_a])+random_value2+bytes(original_a[random_offset_a+length:])

            original_a=bytes(a.buf[:])
            result = a.offset_add_and_fetch(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(random_value1, byteorder='big', signed=False) + \
                int.from_bytes(original_a[random_offset_a:random_offset_a+length], byteorder='big', signed=False)) & int('FF'*length, base=16),
                length=length, byteorder='big')
            assert result == expected
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            original_a=bytes(a.buf[:])
            result = a.offset_sub_and_fetch(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 - int.from_bytes(random_value1, byteorder='big', signed=False)) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == expected
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            original_a=bytes(a.buf[:])
            result = a.offset_and_and_fetch(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 & int.from_bytes(random_value1, byteorder='big', signed=False)) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == expected
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            original_a=bytes(a.buf[:])
            result = a.offset_or_and_fetch(random_value2, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 | int.from_bytes(random_value2, byteorder='big', signed=False)) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == expected
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
            original_a=bytes(a.buf[:])
            result = a.offset_xor_and_fetch(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 ^ int.from_bytes(random_value1, byteorder='big', signed=False)) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == expected
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
            original_a=bytes(a.buf[:])
            result = a.offset_nand_and_fetch(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (~(int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 & int.from_bytes(random_value1, byteorder='big', signed=False))) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == expected
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
            original_a=bytes(a.buf[:])
            result = a.offset_fetch_and_add(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 + int.from_bytes(random_value1, byteorder='big', signed=False)) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == original_a[random_offset_a:random_offset_a+length]
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            original_a=bytes(a.buf[:])
            result = a.offset_fetch_and_sub(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 - int.from_bytes(random_value1, byteorder='big', signed=False)) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == original_a[random_offset_a:random_offset_a+length]
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            original_a=bytes(a.buf[:])
            result = a.offset_fetch_and_and(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 & int.from_bytes(random_value1, byteorder='big', signed=False)) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == original_a[random_offset_a:random_offset_a+length]
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            original_a=bytes(a.buf[:])
            result = a.offset_fetch_and_or(random_value2, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 | int.from_bytes(random_value2, byteorder='big', signed=False)) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == original_a[random_offset_a:random_offset_a+length]
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
            original_a=bytes(a.buf[:])
            result = a.offset_fetch_and_xor(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 ^ int.from_bytes(random_value1, byteorder='big', signed=False)) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == original_a[random_offset_a:random_offset_a+length]
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

            a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
            original_a=bytes(a.buf[:])
            result = a.offset_fetch_and_nand(random_value1, offset=random_offset_a)
            expected = int.to_bytes(
                (~(int.from_bytes(original_a[random_offset_a:random_offset_a + length], byteorder='big', signed=False)
                 & int.from_bytes(random_value1, byteorder='big', signed=False))) & int('FF' * length,
                                                                                                base=16),
                length=length, byteorder='big')
            assert result == original_a[random_offset_a:random_offset_a+length]
            assert bytes(a.buf[:]) == original_a[:random_offset_a]+expected+original_a[random_offset_a+length:]

        original_a=bytes(a.buf[:])
        memmove_length=random.randrange(1, a.size - random_offset_a+1)
        b=array( 'B', b'\0'*memmove_length)
        a.offset_memmove(memoryview(b), offset=random_offset_a, io_flags='o')
        assert bytes(b) == original_a[random_offset_a:random_offset_a+memmove_length]
        b = array('B', os.urandom(memmove_length))
        a.offset_memmove(memoryview(b), offset=random_offset_a, io_flags='i')
        assert bytes(a.buf[:]) == original_a[:random_offset_a]+b[:]+original_a[random_offset_a+memmove_length:]


    #parallellism test
    length_a = 1024 * 2 + 1
    length_b = 1024 * 2 + 1

    lengths=array('b',[1,2,4,8])
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=4096)
    values=array2d(4, 8, 1, signed=True,
                     iterable = [
                         [unsigned2signed(1, i) for i in os.urandom(8)],
                         [unsigned2signed(1, i) for i in os.urandom(8)],
                         [unsigned2signed(1, i)  for i in os.urandom(8)],
                         [unsigned2signed(1, i)  for i in os.urandom(8)]
                     ])
    length_original_a=4

    values_bytes=[]
    for i in range(length_original_a):
        values_bytes.append(b''.join([i.to_bytes(length=1, byteorder='big', signed=True)
                                      for i in values.buf.tolist()[i][:lengths[i]]]))
    other_memories = []
    other_memories.append(atomic_shared_memory(b'1024' * 1024, trimming_direction='l', length=length_b))
    other_memories.append(atomic_shared_memory(b'0241' * 1024, trimming_direction='l', length=length_b))
    other_memories.append(atomic_shared_memory(b'2410' * 1024, trimming_direction='l', length=length_b))
    other_memories.append(atomic_shared_memory(b'4102' * 1024, trimming_direction='l', length=length_b))

    random_offsets_temp_list=[]
    for i in range(length_original_a):
        random_offsets_a_temp = random.randrange(0, length_a - lengths[i])
        for j in range(len(random_offsets_temp_list)):
            while random_offsets_a_temp >= random_offsets_temp_list[j] and random_offsets_a_temp < random_offsets_temp_list[j] + lengths[j] or \
                    random_offsets_a_temp + lengths[i] >= random_offsets_temp_list[j] and random_offsets_a_temp + lengths[i] < random_offsets_temp_list[j] + lengths[j] or \
                    random_offsets_temp_list[j] >= random_offsets_a_temp and random_offsets_temp_list[j] < random_offsets_a_temp + lengths[i] or \
                    random_offsets_temp_list[j] + lengths[j] >= random_offsets_a_temp and random_offsets_temp_list[j] + lengths[j] < random_offsets_a_temp + lengths[i]:
                random_offsets_a_temp = random.randrange(0, length_a - lengths[i])
        random_offsets_temp_list.append(random_offsets_a_temp)

    random_offsets_a=array('Q',random_offsets_temp_list)
    random_offsets_b=array('Q',[random.randrange(0, length_b - length) for length in lengths])
    random_parallelism = random.randrange(0, 2 * os.cpu_count())
    print('random_offsets_a=' + f'{random_offsets_a}')
    print('random_offsets_b=' + f'{random_offsets_b}')
    print('values='+str(values))
    print('lengths='+str(lengths))


    original_a=[b'1024' * 1024, b'1024' * 1024, b'1024' * 1024, b'1024' * 1024]

    expected_result=[]
    for i in range(length_original_a):
        expected_result.append(
            original_a[i][random_offsets_a[i]: random_offsets_a[i]+lengths[i]]+b'\0'*(8-lengths[i])
        )
    result = a.offset_gets(random_offsets_a, lengths, random_parallelism)
    assert bytes(result[:]) == bytes(array2d(4, 8, 1, signed=False, iterable=expected_result).buf[:])

    expected_a=bytearray(original_a[0])
    expected_result=[]
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]]=values_bytes[i]
            #b''.join([i.to_bytes(length=1,byteorder='big', signed=True) for i in values.buf.tolist()[i][:lengths[i]]])
    for i in range(length_original_a):
        expected_result.append(
            original_a[i][random_offsets_a[i]: random_offsets_a[i]+lengths[i]]
        )
    result = a.offset_get_and_sets(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert bytes(a.buf[:]) == expected_a[:]

    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=4096)
    expected_a=bytearray(original_a[0])
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]]=\
            other_memories[i].offset_get(random_offsets_b[i], lengths[i])
    a.offset_stores(other_memories, random_offsets_a, random_offsets_b, lengths, random_parallelism)
    assert bytes(a.buf[:]) == expected_a[:]

    random_offsets_temp_list=[]
    for i in range(length_original_a):
        random_offsets_a_temp = random.randrange(0, length_a - 8)
        for j in range(len(random_offsets_temp_list)):
            while random_offsets_a_temp >= random_offsets_temp_list[j] and random_offsets_a_temp < random_offsets_temp_list[j] + 8 or \
                    random_offsets_a_temp + 8 >= random_offsets_temp_list[j] and random_offsets_a_temp + 8 < random_offsets_temp_list[j] + 8 or \
                    random_offsets_temp_list[j] >= random_offsets_a_temp and random_offsets_temp_list[j] < random_offsets_a_temp + 8 or \
                    random_offsets_temp_list[j] + 8 >= random_offsets_a_temp and random_offsets_temp_list[j] + 8 < random_offsets_a_temp + 8:
                random_offsets_a_temp = random.randrange(0, length_a - 8)
        random_offsets_temp_list.append(random_offsets_a_temp)
    random_offsets_a_temp=array('Q',random_offsets_temp_list)

    '''
    expected_a = bytearray(original_a[0])
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=4096)
    other_objects = []
    max_int=9223372036854775807
    for i in range(length_original_a):
        other_objects.append(atomic_int(random.randrange(-max_int-1, max_int)))
        print("atomic_int.value=", other_objects[i].value)
    for i in range(length_original_a):
        expected_a[random_offsets_a_temp[i]:random_offsets_a_temp[i]+8]=\
                          int.to_bytes(other_objects[i].value, length=8, byteorder='big', signed=True)
    a.offset_stores_from_other_types(other_objects, random_offsets_a_temp, random_parallelism)
    assert bytes(a.buf[:]) == expected_a[:]
    '''

    #original
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    original_a=[(b'1024' * 1024)[:length_a], (b'1024' * 1024)[:length_a], (b'1024' * 1024)[:length_a], (b'1024' * 1024)[:length_a]]
    other_memories = []
    other_memories.append(atomic_shared_memory(b'5555' * 1024, trimming_direction='l', length=length_b))
    other_memories.append(atomic_shared_memory(b'6666' * 1024, trimming_direction='l', length=length_b))
    other_memories.append(atomic_shared_memory(b'7777' * 1024, trimming_direction='l', length=length_b))
    other_memories.append(atomic_shared_memory(b'8888' * 1024, trimming_direction='l', length=length_b))
    original_other_memories = copy.deepcopy([bytes(i.buf[:]) for i in other_memories])
    #expected
    expected_result=[]
    for i in range(length_original_a):
        expected_result.append(
            other_memories[i].buf[random_offsets_b[i]: random_offsets_b[i] + lengths[i]] ==
            a.buf[random_offsets_a[i]: random_offsets_a[i]+ lengths[i]]
        )
        #print(len(other_memories[i].buf))
        #print(len(original_other_memories[i]))

    result = a.offset_compare_and_sets(other_memories, values,
                              random_offsets_a, random_offsets_b,
                              lengths, random_parallelism)
    assert result[:] == expected_result[:]
    assert bytes(a.buf[:]) == original_a[0]
    for i in range(length_original_a):
        #print(len(other_memories[i].buf))
        #print(len(original_other_memories[i]))

        assert bytes(other_memories[i].buf[:]) == original_other_memories[i][:random_offsets_b[i]] + \
                original_a[i][random_offsets_a[i]:random_offsets_a[i] + lengths[i]] + \
                original_other_memories[i][random_offsets_b[i]+ lengths[i]:]


    #a second time expected
    expected_result=[]
    for i in range(length_original_a):
        expected_result.append(
            other_memories[i].buf[random_offsets_b[i]: random_offsets_b[i] + lengths[i]] ==
            a.buf[random_offsets_a[i]: random_offsets_a[i]+ lengths[i]]
        )
    original_other_memories = copy.deepcopy([bytes(i.buf[:]) for i in other_memories])
    result = a.offset_compare_and_sets(other_memories, values,
                              random_offsets_a, random_offsets_b,
                              lengths, random_parallelism)
    assert result[:] == expected_result[:]
    for i in range(length_original_a):
        assert a.buf[random_offsets_a[i]: random_offsets_a[i] + lengths[i]] == values_bytes[i]

    for i in range(length_original_a):
        assert other_memories[i].buf[:] == original_other_memories[i]

    #original
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    ies = array2d(4,8,1, True, [(b'5566' * 1024)[:lengths[3]], (b'6677' * 1024)[:lengths[3]], (b'7788' * 1024)[:lengths[3]], (b'8899' * 1024)[:lengths[3]]])
    nes = array2d(4,8,1,True, [(b'aabb' * 1024)[:lengths[3]], (b'ccdd' * 1024)[:lengths[3]], (b'eeff' * 1024)[:lengths[3]],(b'ffgg' * 1024)[:lengths[3]]])
    original_a = [(b'1024' * 1024)[:length_a], (b'1024' * 1024)[:length_a], (b'1024' * 1024)[:length_a], (b'1024' * 1024)[:length_a]]


    #expected
    expected_result=[]
    for i in range(length_original_a):
        expected_result.append(
            a.buf[random_offsets_a[i]: random_offsets_a[i]+ lengths[i]]
        )
        #print(len(other_memories[i].buf))
        #print(len(original_other_memories[i]))

    result = a.offset_compare_and_set_values(ies, nes, random_offsets_a,lengths, random_parallelism)
    for i in range(length_original_a):
        assert result[i][:lengths[i]] == expected_result[i]
    #assert result[:] == expected_result[:]
    assert bytes(a.buf[:]) == original_a[0]


    #a second time expected
    ies=array2d(4,8,1, True, [(b'aabb' * 1024)[:lengths[3]],
                              (b'ccdd' * 1024)[:lengths[3]],
                              (b'eeff' * 1024)[:lengths[3]],
                              (b'ffgg' * 1024)[:lengths[3]]])
    nes=array2d(4,8,1, True, [(b'1024' * 1024)[random_offsets_a[0]:random_offsets_a[0]+lengths[3]],
                              (b'1024' * 1024)[random_offsets_a[1]:random_offsets_a[1]+lengths[3]],
                              (b'1024' * 1024)[random_offsets_a[2]:random_offsets_a[2]+lengths[3]],
                              (b'1024' * 1024)[random_offsets_a[3]:random_offsets_a[3]+lengths[3]]])
    expected_a = bytearray(original_a[0])
    expected_result=[]
    for i in range(length_original_a):
        expected_result.append(
            bytes(a.buf[random_offsets_a[i]: random_offsets_a[i] + lengths[i]])
        )
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]: random_offsets_a[i] + lengths[i]] =  \
        b''.join([j.to_bytes(length=1, byteorder='big', signed=True)
                                      for j in ies.buf.tolist()[i][:lengths[i]]])
    result = a.offset_compare_and_set_values(ies, nes, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert bytes(a.buf[:]) == expected_a

    expected_a = bytearray(original_a[0])
    expected_result=[]
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(
                          int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) + \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
        )
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = expected_result[i]
    result = a.offset_add_and_fetches(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result=[]
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(
                          int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) - \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
        )
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = expected_result[i]
    result = a.offset_sub_and_fetches(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result=[]
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(
                          int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) & \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
        )
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = expected_result[i]
    result = a.offset_and_and_fetches(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result=[]
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(
                          int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) | \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
        )
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = expected_result[i]
    result = a.offset_or_and_fetches(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result=[]
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(
                          int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) ^ \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
        )
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = expected_result[i]
    result = a.offset_xor_and_fetches(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result=[]
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(
                          (int.to_bytes(
                              (~(int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) & \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False))) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
        ))
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = expected_result[i]
    result = a.offset_nand_and_fetches(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result=[]
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]])
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = \
            int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) + \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
    result = a.offset_fetch_and_adds(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result=[]
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]])
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = \
            int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) - \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
    result = a.offset_fetch_and_subs(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result = []
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]])
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = \
            int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) & \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
    result = a.offset_fetch_and_ands(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result = []
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]])
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = \
            int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) | \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
    result = a.offset_fetch_and_ors(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result = []
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]])
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = \
            int.to_bytes((int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) ^ \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False)) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
    result = a.offset_fetch_and_xors(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    expected_a = bytearray(original_a[0])
    expected_result=[]
    a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=length_a)
    for i in range(length_original_a):
        expected_result.append(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]])
    for i in range(length_original_a):
        expected_a[random_offsets_a[i]:random_offsets_a[i]+lengths[i]] = \
            int.to_bytes((~(
                           int.from_bytes(original_a[i][random_offsets_a[i]:random_offsets_a[i]+lengths[i]], byteorder='big', signed=False) & \
                           int.from_bytes(values_bytes[i], byteorder='big',signed=False))) & int('FF' * lengths[i], base=16), length=lengths[i], byteorder='big')
    result = a.offset_fetch_and_nands(values, random_offsets_a, lengths, random_parallelism)
    for i in range(length_original_a):
        assert bytes(result[i][:lengths[i]]) == expected_result[i]
    assert a.buf[:] == expected_a[:]

    '''
    pytest.raises(ValueError, a.offset_stores, b, random_offset_a, random_offset_b, length)
    pytest.raises(ValueError, a.offset_stores_from_other_types, b, b'abc', random_offset_a, random_offset_a)
    pytest.raises(ValueError, a.offset_compare_and_sets, b'abc', b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_add_and_fetches, b'abcd', b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_add_and_fetch, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_sub_and_fetch, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_and_and_fetch, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_or_and_fetch, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_xor_and_fetch, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_nand_and_fetch, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_nand_and_fetch, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_fetch_and_add, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_fetch_and_sub, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_fetch_and_and, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_fetch_and_or, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_fetch_and_xor, b'abd', random_offset_a)
    pytest.raises(ValueError, a.offset_fetch_and_nand, b'abd', random_offset_a)
    '''

def test_offset_get():
    random_parallelism = random.randrange(0, 2 * os.cpu_count())
    a = atomic_shared_memory(b'1024abcd5678efgh1011', mode='m')
    assert a.offset_get(1,6) == b'024abc'
    assert a.offset_get(2,3) == b'24a'
    assert a.offset_get(8,2) == b'56'
    assert pytest.raises(ValueError, a.offset_get, 2,10)
    assert shared_memory_offset_get(a, 1,6) == b'024abc'
    assert shared_memory_offset_get(a, 2,3) == b'24a'
    assert shared_memory_offset_get(a, 8,2) == b'56'
    assert pytest.raises(ValueError, shared_memory_offset_get, a, 2,10)

    original_a = [b'1024abcd5678efgh1011', b'1024abcd5678efgh1011',
                  b'1024abcd5678efgh1011', b'1024abcd5678efgh1011']

    random_offsets_a = array('Q', [1,2,8,7])
    lengths = array('b', [6,3,2,2])
    expected_result = []
    for i in range(4):
        expected_result.append(
            original_a[i][random_offsets_a[i]: random_offsets_a[i] + lengths[i]] + b'\0' * (8 - lengths[i]))
    result = a.offset_gets(random_offsets_a, lengths, random_parallelism)
    for i in range(4):
        assert bytes(result[i][:lengths[i]]) + b'\0' * (8 - lengths[i])== expected_result[i]


def thread_run(a,):
    if a.offset_compare_and_set_value(b'bc', b'cd', 2) == b'bc':
        assert a.offset_get(0, 4) == b'abbc'

def test_thread_atomic():
    """
    test single process multiple threads
    :return: None
    """
    a = atomic_shared_memory(b'abcd', mode='s', length=1024 ** 3)
    threadlist = []
    for i in range(10000):
        threadlist.append(Thread(target=thread_run, args=(a,)))
    for i in range(10000):
        threadlist[i].start()
    for i in range(10000):
        threadlist[i].join()
    assert a.offset_get(0,2) == b'ab'


def process_run_compatibility(a: atomic_shared_memory):
    def subthread_run(a: atomic_shared_memory):
        if a.offset_compare_and_set_value(b'bc',b'cd',2) == b'cd':
            assert a.offset_get(0,4) == b'abbc'

    threadlist = []
    for t in range(5000):
        threadlist.append(Thread(target=subthread_run, args=(a,)))

    for t in range(5000):
        threadlist[t].start()

    for t in range(5000):
        threadlist[t].join()


def test_process_atomic_compatibility():
    """
    test multiple processes
    :return: None
    """
    a = atomic_shared_memory(b'abcd', mode='m', length=1024 ** 3, windows_unix_compatibility=True)

    processlist = []
    for i in range(2):
        processlist.append(Process(target=process_run_compatibility, args=(a,)))

    for i in range(2):
        processlist[i].start()

    for i in range(2):
        processlist[i].join()

    assert a.offset_get(0, 4) == b'abbc'

def process_run(a):
    def subthread_run(a):
        if shared_memory_offset_compare_and_set_value(a, b'bc', b'cd', 2) == b'cd':
            assert shared_memory_offset_get(a, 0, 4) == b'abbc'

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
        a = atomic_shared_memory(b'abcd', mode='m', length=1024 ** 3, windows_unix_compatibility=False)
        processlist = []

        for i in range(10):
            processlist.append(Process(target=process_run, args=(a,)))

        for i in range(10):
            processlist[i].start()

        for i in range(10):
            processlist[i].join()

        assert a.offset_get(0, 4) == b'abbc'