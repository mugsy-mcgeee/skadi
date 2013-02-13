from google.protobuf.message import DecodeError

def _VarintDecoder(mask):
  local_ord = ord
  def DecodeVarint(buffer, pos):
    result = 0
    shift = 0
    while 1:
      b = local_ord(buffer[pos])
      result |= ((b & 0x7f) << shift)
      pos += 1
      if not (b & 0x80):
        result &= mask
        return (result, pos)
      shift += 7
      if shift >= 64:
        raise DecodeError('Too many bytes when decoding varint.')
  return DecodeVarint

def _SignedVarintDecoder(mask):
  """Like _VarintDecoder() but decodes signed values."""

  local_ord = ord
  def DecodeVarint(buffer, pos):
    result = 0
    shift = 0
    while 1:
      b = local_ord(buffer[pos])
      result |= ((b & 0x7f) << shift)
      pos += 1
      if not (b & 0x80):
        if result > 0x7fffffffffffffff:
          result -= (1 << 64)
          result |= ~mask
        else:
          result &= mask
        return (result, pos)
      shift += 7
      if shift >= 64:
        raise DecodeError('Too many bytes when decoding varint.')
  return DecodeVarint

_DecodeVarint         = _VarintDecoder((1 << 64) - 1)
_DecodeSignedVarint   = _SignedVarintDecoder((1 << 64) - 1)
_DecodeVarint32       = _VarintDecoder((1 << 32) - 1)
_DecodeSignedVarint32 = _SignedVarintDecoder((1 << 32) - 1)

