from skadi.core.parser import Parser
from skadi.cli.delegate import RecordsMessages

class ProcessesPackets(object):
    def __call__(self, msg, obj):
        parser   = Parser(obj)
        delegate = RecordsMessages()

        parser.register(delegate, Parser.PacketEntities)
        parser.parse()
