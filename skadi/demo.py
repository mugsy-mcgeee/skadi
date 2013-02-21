from skadi import *

import os, sys, snappy

import skadi.generated.demo_pb2 as demo_pb2
import skadi.generated.netmessages_pb2 as netmessages_pb2

class Demo(object):
    Nothing             = 0x0000
    Everything          = 0xffff
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

    CMD_TO_SPEC = {
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
        self.path      = path
        self.file      = None
        self.delegates = []

    def register(self, callback, mask = Everything):
        self.delegates.append([callback, mask])

    def parse(self):
        self._open()

        self.file.seek(12) # skip demo header

        while True:
            cmd_tell, cmd_meta = self.file.tell(), self.file.read(12)
            if len(cmd_meta) == 0:
                break

            cmd,      cmd_pos = decode_varint(cmd_meta,       0)
            cmd_tick, cmd_pos = decode_varint(cmd_meta, cmd_pos)
            cmd_size, cmd_pos = decode_varint(cmd_meta, cmd_pos)

            self.file.seek(cmd_tell + cmd_pos, 0)
            cmd_data = self.file.read(cmd_size)

            compressed = \
                (demo_pb2.DEM_IsCompressed & cmd == demo_pb2.DEM_IsCompressed)
            if compressed:
                cmd      = cmd ^ demo_pb2.DEM_IsCompressed
                cmd_data = snappy.uncompress(cmd_data)

            try:
                message, pbmsg = Demo.CMD_TO_SPEC[cmd]
            except KeyError:
                message, pbmsg = Demo.Unhandled, None

            obj = pbmsg()
            obj.ParseFromString(cmd_data)

            expecting = [s[0] for s in self.delegates if (s[-1] & message)]
            [delegate(message, obj) for delegate in expecting]

        self._close()

    def _open(self):
        self.file = open(self.path, 'rb')

    def _close(self):
        self.file.close()
        self.file = None
