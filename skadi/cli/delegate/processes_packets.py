from skadi.cli.delegate import RecordsMessages
from skadi.core.parser.packet import Packet
from skadi.cli.model.server_entity import ServerEntity

class ProcessesPackets(object):
    def __init__(self):
        self.server_entities = []

    def __call__(self, msg, obj):
        parser   = Packet(obj)
        delegate = RecordsMessages()

        parser.register(delegate) # for everything
        parser.parse()

        for capture in delegate.captures[Packet.PacketEntities]:
            # print capture.updated_entries
            # out = ''.join(bin(ord(c))[2:].zfill(8) for c in capture.entity_data)
            # print out
            # print
            pass