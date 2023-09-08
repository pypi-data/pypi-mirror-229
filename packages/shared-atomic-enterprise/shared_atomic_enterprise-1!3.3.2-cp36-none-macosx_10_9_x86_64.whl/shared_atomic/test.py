from array import array
from shared_atomic.atomic_object import array2d
from shared_atomic.atomic_shared_memory import atomic_shared_memory
original_a = [b'1024' * 1024, b'1024' * 1024, b'1024' * 1024, b'1024' * 1024]
lengths=array('b', [1, 2, 4, 8])
length_original_a=4
random_offsets_a=array('Q', [344, 161, 27, 380])
random_offsets_b=array('Q', [1014, 467, 1861, 705])
expected_result = []
for i in range(length_original_a):
    expected_result.append(
        original_a[i][random_offsets_a[i]: random_offsets_a[i] + lengths[i]] + b'\0' * (8 - lengths[i])
    )

a = atomic_shared_memory(b'1024' * 1024, mode='m', trimming_direction='r', length=4096)
result = a.offset_gets(random_offsets_a, lengths, 4)
assert bytes(result[:]) == bytes(array2d(4, 8, 1, signed=False, iterable=expected_result).buf[:])


for i in result:
    for j in result[i]:
        print(result[i][j])