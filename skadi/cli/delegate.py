from skadi.core.parser import Parser
from skadi.model.table import SendTable

class RecordsMessages(object):
    def __init__(self):
        self.captures = {}

    def __call__(self, message, obj):
        if not message in self.captures:
            self.captures[message] = []
        self.captures[message].append(obj)

    def recorded_messages(self):
        return self.captures.keys()

class CreatesSendTables(object):
    def __init__(self):
        self.send_tables = []

    def __call__(self, msg, obj):
        parser   = Parser(obj)
        delegate = RecordsMessages()

        parser.register(delegate) # for everything
        parser.parse()

        for capture in delegate.captures[Parser.SendTable]:
            st = SendTable(capture)
            if not st.is_last:
                self.send_tables.append(st)

class ProcessesPackets(object):
    def __call__(self, msg, obj):
        parser   = Parser(obj)
        delegate = RecordsMessages()

        parser.register(delegate, Parser.PacketEntities)
        parser.parse()
