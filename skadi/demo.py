import collections
import copy
import io
import math
import pprint

from skadi.engine import *
from skadi.engine import bitstream as bs
from skadi.engine.unpacker import entity as uent
from skadi.index import demo as di
from skadi.index import packet as pi
from skadi.protoc import demo_pb2 as pb_d
from skadi.protoc import netmessages_pb2 as pb_n


HEADER = "PBUFDEM\0"


class InvalidDemo(RuntimeError):
  pass


def construct(io):
  io.seek(0)

  if io.read(len(HEADER)) != HEADER:
    raise InvalidDemo('malformed header')

  io.read(4) # game summary offset in file in bytes

  return Demo(io, di.index(io))


class Stream(object):
  def __init__(self, demo_index, string_tables, entities):
    pass


class Demo(object):
  def __init__(self, io, index):
    self.io = io
    self.index = index
 
  def bootstrap(self):
    prologue_index = self.index.prologue

    cdemo_file_header = di.read(self.io, prologue_index.file_header_peek)
    self.file_header = parse_cdemo_file_header(cdemo_file_header)

    cdemo_class_info = di.read(self.io, prologue_index.class_info_peek)
    self.class_info = parse_cdemo_class_info(cdemo_class_info)

    cdemo_send_tables = di.read(self.io, prologue_index.send_tables_peek)
    self.send_tables = parse_cdemo_send_tables(cdemo_send_tables)
    self.recv_tables = flatten(self.class_info, self.send_tables)

    # for prologue packets, concat and index their data for easy access
    prologue_cdemo_packets = \
      [di.read(self.io, p) for p in prologue_index.packet_peeks]

    cdemo_packet_data = ''.join([cdp.data for cdp in prologue_cdemo_packets])
    p_io = io.BufferedReader(io.BytesIO(cdemo_packet_data))
    packet_index = pi.index(p_io)

    csvc_create_string_table_peeks = \
      packet_index.find_all(pb_n.CSVCMsg_CreateStringTable)
    all_csvc_create_string_table = \
      [pi.read(p_io, peek) for peek in csvc_create_string_table_peeks]
    self.string_tables = \
      parse_all_csvc_create_string_table(all_csvc_create_string_table)

    csvc_voice_init = pi.read(p_io, packet_index.find(pb_n.CSVCMsg_VoiceInit))
    self.voice_init = parse_csvc_voice_init(csvc_voice_init)

    csvc_server_info = \
      pi.read(p_io, packet_index.find(pb_n.CSVCMsg_ServerInfo))
    self.server_info = parse_csvc_server_info(csvc_server_info)

    csvc_game_event_list = \
      pi.read(p_io, packet_index.find(pb_n.CSVCMsg_GameEventList))
    self.game_event_list = parse_csvc_game_event_list(csvc_game_event_list)

    max_classes = self.server_info['max_classes']
    self.class_bits = int(math.ceil(math.log(max_classes, 2)))

  def stream(self, tick=0):
    match = self.index.match
    state = filter(lambda peek: peek.tick < tick, match.full_packet_peeks)

    string_tables = copy.deepcopy(self.string_tables)
    entities = collections.OrderedDict()

    for peek in state:
      full_packet = di.read(self.io, peek)
      string_table_updates = full_packet.string_table.tables

      for table in string_table_updates:
        assert not table.items_clientside # unsupported, not used

        pick = table.table_name
        entries = [(i, _i.str, _i.data) for i, _i in enumerate(table.items)]

        mapped = map(lambda (i,n,d): (i,(n,d)), entries)
        string_tables[pick]['by_index'] = collections.OrderedDict(mapped)

        mapped = map(lambda (i,n,d): (n,(i,d)), entries)
        string_tables[pick]['by_name'] = collections.OrderedDict(mapped)

    full_packet = di.read(self.io, state[-1])
    p_io = io.BufferedReader(io.BytesIO(full_packet.packet.data))
    packet = pi.index(p_io)

    csvc_packet_entities = \
      pi.read(p_io, packet.find(pb_n.CSVCMsg_PacketEntities))

    bitstream = bs.construct(csvc_packet_entities.entity_data)
    ct = csvc_packet_entities.updated_entries
    cb, rt = self.class_bits, self.recv_tables

    entities = collections.OrderedDict()
    unpacker = uent.Unpacker(bitstream, -1, ct, False, cb, rt, {})
    baselines = string_tables['instancebaseline']

    for mode, index, context in list(unpacker):
      assert mode == uent.PVS.Entering

      cls, serial, diff = context

      bitstream = bs.construct(baselines['by_name'][cls][1]) # baseline data
      _unpacker = uent.Unpacker(bitstream, -1, 1, False, cb, rt, {})
      state = _unpacker.unpack_baseline(self.recv_tables[cls])
      state.update(diff)

      print index, self.recv_tables[cls]
      pp = pprint.PrettyPrinter(depth=2)
      pp.pprint(state)

      entities[index] = (cls, serial, state)

