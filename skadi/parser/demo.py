import os, sys, snappy
import skadi.parser as parser

import skadi.generated.demo_pb2 as demo_pb2

class Demo(object):
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

	MAP = {
		demo_pb2.DEM_Stop:                Stop,
		demo_pb2.DEM_FileHeader:          FileHeader,
		demo_pb2.DEM_FileInfo:            FileInfo,
		demo_pb2.DEM_SyncTick:            SyncTick,
		demo_pb2.DEM_SendTables:          SendTables,
		demo_pb2.DEM_ClassInfo:           ClassInfo,
		demo_pb2.DEM_StringTables:        StringTables,
		demo_pb2.DEM_Packet:              Packet,
		demo_pb2.DEM_SignonPacket:        SignonPacket,
		demo_pb2.DEM_ConsoleCmd:          ConsoleCmd,
		demo_pb2.DEM_CustomData:          CustomData,
		demo_pb2.DEM_CustomDataCallbacks: CustomDataCallbacks,
		demo_pb2.DEM_UserCmd:             UserCmd,
		demo_pb2.DEM_FullPacket:          FullPacket
	}

	def __init__(self, path):
		self.path        = path
		self.file        = None
		self.subscribers = []

	def subscribe(self, callback, mask = 0xffff):
		self.subscribers.append([callback, mask])

	def parse(self):
		self._open()

		self.file.seek(12)

		while True:
			cmd_tell = self.file.tell()
			cmd_meta = parser._buffer(self.file, pos = 0, to = 18)
			if len(cmd_meta) == 0:
				break

			cmd,      cmd_pos = parser.decode_varint_32(cmd_meta,       0)
			cmd_tick, cmd_pos = parser.decode_varint_32(cmd_meta, cmd_pos)
			cmd_size, cmd_pos = parser.decode_varint_32(cmd_meta, cmd_pos)

			compressed = demo_pb2.DEM_IsCompressed & cmd
			cmd_data   = parser._buffer(self.file, cmd_meta, pos = cmd_pos, to = cmd_size)

			if compressed:
				cmd      = cmd & ~demo_pb2.DEM_IsCompressed
				cmd_data = snappy.uncompress(cmd_data)

			try:
				message = Demo.MAP[cmd]
			except KeyError:
				message = Demo.Unhandled

			expecting = [s[0] for s in self.subscribers if (s[-1] & message)]
			[callback(message, cmd_data, {}) for callback in expecting]

			self.file.seek(cmd_tell + cmd_pos + cmd_size, 0)

		self._close()

	def _open(self):
		self.file = open(self.path, 'rb')

	def _close(self):
		self.file.close()
		self.file = None
