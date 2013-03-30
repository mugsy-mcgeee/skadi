import os, sys, snappy

import skadi.generated.demo_pb2 as demo_pb2
import skadi.generated.netmessages_pb2 as netmessages_pb2

from skadi.core import decode_varint
from skadi.core.dispatcher import Dispatcher

class Demo(Dispatcher):
    Stop                = 1 <<  0
    FileHeader          = 1 <<  1
    FileInfo            = 1 <<  2
    SyncTick            = 1 <<  3
    SendTables          = 1 <<  4
    ClassInfo           = 1 <<  5
    StringTables        = 1 <<  6
    Packet              = 1 <<  7
    SignonPacket        = 1 <<  8
    ConsoleCmd          = 1 <<  9
    CustomData          = 1 << 10
    CustomDataCallbacks = 1 << 11
    UserCmd             = 1 << 12
    FullPacket          = 1 << 13
    Unhandled           = 1 << 15

    MESSAGE_TO_SPEC = {
        demo_pb2.DEM_Stop: (Stop, demo_pb2.CDemoStop),
        demo_pb2.DEM_FileHeader: (FileHeader, demo_pb2.CDemoFileHeader),
        demo_pb2.DEM_FileInfo: (FileInfo, demo_pb2.CDemoFileInfo),
        demo_pb2.DEM_SyncTick: (SyncTick, demo_pb2.CDemoFileInfo),
        demo_pb2.DEM_SendTables: (SendTables, demo_pb2.CDemoSendTables),
        demo_pb2.DEM_ClassInfo: (ClassInfo, demo_pb2.CDemoClassInfo),
        demo_pb2.DEM_StringTables: (StringTables, demo_pb2.CDemoStringTables),
        demo_pb2.DEM_Packet: (Packet, demo_pb2.CDemoPacket),
        demo_pb2.DEM_SignonPacket: \
            (SignonPacket, netmessages_pb2.CNETMsg_SignonState),
        demo_pb2.DEM_ConsoleCmd: (ConsoleCmd, demo_pb2.CDemoConsoleCmd),
        demo_pb2.DEM_CustomData: (CustomData, demo_pb2.CDemoCustomData),
        demo_pb2.DEM_CustomDataCallbacks: \
            (CustomDataCallbacks, demo_pb2.CDemoCustomDataCallbacks),
        demo_pb2.DEM_UserCmd: (UserCmd, demo_pb2.CDemoUserCmd),
        demo_pb2.DEM_FullPacket: (FullPacket, demo_pb2.CDemoFullPacket)
    }

    def __init__(self, path):
        super(Demo,self).__init__()
        self._path = path
        self._file = None

    def parse(self):
        self._open()

        self._file.seek(12) # skip demo header

        while True:
            cmd_tell, cmd_meta = self._file.tell(), self._file.read(12)
            if len(cmd_meta) == 0:
                break

            cmd,      cmd_pos = decode_varint(cmd_meta,       0)
            cmd_tick, cmd_pos = decode_varint(cmd_meta, cmd_pos)
            cmd_size, cmd_pos = decode_varint(cmd_meta, cmd_pos)

            self._file.seek(cmd_tell + cmd_pos, 0)
            cmd_data = self._file.read(cmd_size)

            compressed = \
                (demo_pb2.DEM_IsCompressed & cmd == demo_pb2.DEM_IsCompressed)
            if compressed:
                cmd      = cmd ^ demo_pb2.DEM_IsCompressed
                cmd_data = snappy.uncompress(cmd_data)

            try:
                message, pbmsg = Demo.MESSAGE_TO_SPEC[cmd]

                obj = pbmsg()
                obj.ParseFromString(cmd_data)
            except KeyError:
                message, obj = Dispatcher.Unhandled, None

            self.dispatch(message, obj)

        self._close()

    def _open(self):
        self._file = open(self._path, 'rb')

    def _close(self):
        self._file.close()
        self._file = None
