from google.protobuf.message import DecodeError

def _buffer(src, buf= '', pos = 0, to = 1024):
	"""
	Given a buffer (i.e. a string), grow it to the desired size,
	reading appropriately from src.
	"""
	deficit = to - (len(buf) - pos)
	if deficit < 0:
		return buf[pos:]
	return buf[pos:] + src.read(deficit)

def _varint_decoder(mask):
  local_ord = ord
  def decode_varint(buffer, pos):
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
  return decode_varint

decode_varint    = _varint_decoder((1 << 64) - 1)
decode_varint_32 = _varint_decoder((1 << 32) - 1)
