from skadi.core.parser import Parser
from skadi.model.dt import DT

class RecordsMessages(object):
    def __init__(self):
        self.captures = {}

    def __call__(self, message, obj):
        if not message in self.captures:
            self.captures[message] = []
        self.captures[message].append(obj)

    def recorded_messages(self):
        return self.captures.keys()

class CreatesDTs(object):
    def __init__(self):
        self.dts = []

    def __call__(self, msg, obj):
        parser   = Parser(obj)
        delegate = RecordsMessages()

        parser.register(delegate) # for everything
        parser.parse()

        for capture in delegate.captures[Parser.SendTable]:
            self.dts.append(DT(capture))

class ProcessesPackets(object):
    def __call__(self, msg, obj):
        parser   = Parser(obj)
        delegate = RecordsMessages()

        parser.register(delegate, Parser.PacketEntities)
        parser.parse()
