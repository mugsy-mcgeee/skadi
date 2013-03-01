import skadi.core as core
from skadi.core.dispatcher import Dispatcher

import skadi.generated.netmessages_pb2 as netmessages_pb2

class Parser(Dispatcher):
    ClassInfo      = 1 <<  0
    SendTable      = 1 <<  1
    PacketEntities = 1 <<  2
    TempEntities   = 1 <<  3

    MESSAGE_TO_SPEC = {
        netmessages_pb2.svc_ClassInfo:      (ClassInfo,      netmessages_pb2.CSVCMsg_ClassInfo     ),
        netmessages_pb2.svc_SendTable:      (SendTable,      netmessages_pb2.CSVCMsg_SendTable     ),
        netmessages_pb2.svc_PacketEntities: (PacketEntities, netmessages_pb2.CSVCMsg_PacketEntities),
        netmessages_pb2.svc_TempEntities:   (TempEntities,   netmessages_pb2.CSVCMsg_TempEntities  )
    }

    def __init__(self, obj):
        super(Parser,self).__init__()
        self.obj = obj

    def parse(self):
        data    = self.obj.data
        msg_pos = 0

        while True:
            if msg_pos == len(data):
                break

            msg,      msg_pos = core.decode_varint(data, msg_pos)
            msg_size, msg_pos = core.decode_varint(data, msg_pos)

            msg_data = data[msg_pos:msg_pos+msg_size]

            try:
                message, pbmsg = Parser.MESSAGE_TO_SPEC[msg]

                obj = pbmsg()
                obj.ParseFromString(msg_data)
            except KeyError:
                message, obj = Dispatcher.Unhandled, None

            self.dispatch(message, obj)

            msg_pos += msg_size
