from skadi import *
from skadi.dispatcher import Dispatcher

import skadi.generated.netmessages_pb2 as netmessages_pb2

class SendTables(Dispatcher):
    SendTable = 1 <<  0

    MESSAGE_TO_SPEC = {
        netmessages_pb2.svc_SendTable: (SendTable, netmessages_pb2.CSVCMsg_SendTable)
    }

    def __init__(self, obj):
        super(SendTables,self).__init__()
        self.obj = obj

    def parse(self):
        data    = self.obj.data
        msg_pos = 0

        while True:
            if msg_pos == len(data):
                break

            msg,      msg_pos = decode_varint(data, msg_pos)
            msg_size, msg_pos = decode_varint(data, msg_pos)

            msg_data = data[msg_pos:msg_pos+msg_size]

            try:
                message, pbmsg = SendTables.MESSAGE_TO_SPEC[msg]

                obj = pbmsg()
                obj.ParseFromString(msg_data)
            except KeyError:
                message, obj = Dispatcher.Unhandled, None

            self.dispatch(message, obj)

            msg_pos += msg_size
