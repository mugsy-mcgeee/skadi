import collections
import snappy

from skadi.index import InvalidProtobufMessage, Index
from skadi.io import read_varint
from skadi.protoc import demo_pb2 as pb_d


test_full_packet = lambda p: p.cls is pb_d.CDemoFullPacket
test_packet = lambda p: p.cls is pb_d.CDemoPacket


PBMSG_BY_ENUM = {
  pb_d.DEM_Stop:                pb_d.CDemoStop,
  pb_d.DEM_FileHeader:          pb_d.CDemoFileHeader,
  pb_d.DEM_FileInfo:            pb_d.CDemoFileInfo,
  pb_d.DEM_SendTables:          pb_d.CDemoSendTables,
  pb_d.DEM_SyncTick:            pb_d.CDemoSyncTick,
  pb_d.DEM_ClassInfo:           pb_d.CDemoClassInfo,
  pb_d.DEM_StringTables:        pb_d.CDemoStringTables,
  pb_d.DEM_Packet:              pb_d.CDemoPacket,
  pb_d.DEM_SignonPacket:        pb_d.CDemoPacket,
  pb_d.DEM_ConsoleCmd:          pb_d.CDemoConsoleCmd,
  pb_d.DEM_CustomData:          pb_d.CDemoCustomData,
  pb_d.DEM_CustomDataCallbacks: pb_d.CDemoCustomDataCallbacks,
  pb_d.DEM_UserCmd:             pb_d.CDemoUserCmd,
  pb_d.DEM_FullPacket:          pb_d.CDemoFullPacket
}


peek_attrs = ['tick', 'cls', 'offset', 'size', 'compressed']
Peek = collections.namedtuple('Peek', peek_attrs)


def construct(stream):
  return DemoIndex(Indexer(stream))


def read(stream, peek):
  if peek.cls not in PBMSG_BY_ENUM.values():
    msg = 'please update demo.proto: {0}'.format(peek.cls)
    raise InvalidProtobufMessage(msg)

  stream.seek(peek.offset)

  data = stream.read(peek.size)
  if peek.compressed:
    data = snappy.uncompress(data)

  message = peek.cls()
  message.ParseFromString(data)

  return message


class DemoIndex(Index):
  def __init__(self, iterable):
    super(DemoIndex, self).__init__(iterable)

  @property
  def prologue(self):
    peek = self.find(pb_d.CDemoSyncTick)
    return PrologueIndex(self.find_behind(peek.offset))

  @property
  def match(self):
    b = self.find_behind(self._stop.offset)
    a = self.find_ahead(self._sync.offset)
    i = list(set(a) & set(b))
    return MatchIndex(sorted(i, key=lambda p: p.tick))

  @property
  def epilogue(self):
    peek = self.find(pb_d.CDemoStop)
    return EpilogueIndex(self.find_ahead(peek.offset))

  @property
  def _sync(self):
    return self.find(pb_d.CDemoSyncTick)

  @property
  def _stop(self):
    return self.find(pb_d.CDemoStop)


class PrologueIndex(Index):
  def __init__(self, iterable):
    super(PrologueIndex, self).__init__(iterable)

  @property
  def class_info_peek(self):
    return self.find(pb_d.CDemoClassInfo)

  @property
  def file_header_peek(self):
    return self.find(pb_d.CDemoFileHeader)

  @property
  def send_tables_peek(self):
    return self.find(pb_d.CDemoSendTables)

  @property
  def packet_peeks(self):
    return self.find_all(pb_d.CDemoPacket)


class MatchIndex(Index):
  def __init__(self, iterable):
    super(MatchIndex, self).__init__(iterable)
    self.full_ticks = map(lambda p: p.tick, self.full_packet_peeks)
    self.ticks = map(lambda p: p.tick, self.packet_peeks)[1:]
    self._ft, self._t = None, None

  def find_earlier(self, tick):
    return filter(lambda p: p.tick < tick, self.peeks)

  def find_when(self, tick):
    return filter(lambda p: p.tick == tick, self.peeks)

  def find_later(self, tick):
    return filter(lambda p: p.tick > tick, self.peeks)

  def locate_full_tick(self, near):
    self._ft = self._ft or list(reversed(self.full_ticks))
    return next(t for t in self._ft if t < near)

  def locate_tick(self, near):
    self._t = self._t or list(reversed(self.ticks))
    try:
      tick = next(t for t in self._t if t <= near)
    except StopIteration:
      tick = self.ticks[0]
    return tick

  def locate(self, near):
    return self.locate_full_tick(tick), self.locate_tick(tick)

  def locate_between(self, low, high):
    return (t for t in self.ticks if t > low and t <= high)

  def lookup_full(self, tick):
    when = self.find_when(tick)
    return next((p for p in when if test_full_packet(p)), None)

  def lookup(self, tick):
    when = self.find_when(tick)
    return next((p for p in when if test_packet(p)), None)

  @property
  def full_packet_peeks(self):
    return filter(test_full_packet, self.peeks)

  @property
  def packet_peeks(self):
    return filter(test_packet, self.peeks)


class EpilogueIndex(Index):
  def __init__(self, iterable):
    super(EpilogueIndex, self).__init__(iterable)

  @property
  def file_info_peek(self):
    return self.find(pb_d.CDemoFileInfo)


class Indexer(object):
  def __init__(self, stream):
    self.stream = stream

  def __iter__(self):
    def next():
      return self.next()
    return iter(next, None)

  def next(self):
    start = self.stream.tell()

    try:
      enum = read_varint(self.stream)
      tick = read_varint(self.stream)
      size = read_varint(self.stream)

      compressed = (pb_d.DEM_IsCompressed & enum) == pb_d.DEM_IsCompressed
      enum = (enum ^ pb_d.DEM_IsCompressed) if compressed else enum

      offset = self.stream.tell()

      self.stream.seek(offset + size)
    except EOFError, e:
      return None

    cls, o, s, c = PBMSG_BY_ENUM[enum], offset, size, compressed

    return Peek(tick=tick, cls=cls, offset=o, size=s, compressed=c)
