from skadi.core.parser import Parser
from skadi.model.table import SendTable, Proplist
from skadi.model.prop import Prop

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

        for c in delegate.captures[Parser.SendTable]:
            if not c.is_end:
                name     = c.net_table_name
                proplist = Proplist([Prop(name, p) for p in c.props])
                st       = SendTable(name, proplist, is_leaf=c.needs_decoder)
                self.send_tables.append(st)

class ProcessesPackets(object):
    def __call__(self, msg, obj):
        parser   = Parser(obj)
        delegate = RecordsMessages()

        parser.register(delegate, Parser.PacketEntities)
        parser.parse()
