import skadi.core as core
from skadi.core.dispatcher import Dispatcher

import skadi.generated.netmessages_pb2 as netmessages_pb2

class Packet(Dispatcher):
    PacketEntities = 1 <<  0

    MESSAGE_TO_SPEC = {
        netmessages_pb2.svc_PacketEntities: (PacketEntities, netmessages_pb2.CSVCMsg_PacketEntities)
    }

    def __init__(self, obj):
        super(Packet,self).__init__()
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
                message, pbmsg = Packet.MESSAGE_TO_SPEC[msg]

                obj = pbmsg()
                obj.ParseFromString(msg_data)
            except KeyError:
                message, obj = Dispatcher.Unhandled, None

            self.dispatch(message, obj)

            msg_pos += msg_size
