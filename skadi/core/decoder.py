from bitstring import Bits
from bitstring import ConstBitStream


def _read_var_uint(data):
    encoded = 0x30

    hdr = data.read('uint:6')
    print 'hdr={}'.format(hdr)

    if hdr == encoded:
        edx = (2 - ((hdr >> 4) & 3)) >> 0x1F
        print 'edx({}) = (2 - ((hdr >> 4) & 3)) >> 0x1F'.format(edx)
        edx = edx & 0x10
        print 'edx({}) = edx & 0x10'.format(edx)
        edi = edx + hdr * 4
        print 'edi({}) = edx + hdr * 4'.format(edi)

        value = (data.read('uint:{}'.format(edi)) << 4) | (hdr & 15)
    else:
        return hdr


def _read_var_int(data):
    count = 0
    result = 0
    next_byte = data.read('int:6')
    print 'next_byte = {}'.format(next_byte)
    result |= (next_byte & 0x1F) << (5 * count)
    print 'result = {}'.format(result)

    while next_byte & 0x20 == 1:
        count += 1
        if count == 5:
            raise Exception('Suspect corrupt data')
        else:
            next_byte = data.read('int:6')
            print 'next_byte = {}'.format(next_byte)
            result |= (next_byte & 0x1F) << (5 * count)
            print 'result = {}'.format(result)

    return result


def decode_entity(data_string):
    "Accepts raw data of binary object data and returns decoded data"
    data = ConstBitStream(Bits(bytes=data_string))
    print '{}\n'.format(data.peek('bin:32'))
    base = -1
    ent_id = base + 1 + _read_var_int(data)
    print 'ent_id={}'.format(ent_id)
