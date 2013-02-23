from skadi.cli.delegate import RecordsMessages
from skadi.core.parser.send_tables import SendTables
from skadi.cli.model.server_entity import ServerEntity

class CreatesServerEntities(object):
    def __init__(self):
        self.server_entities = []

    def __call__(self, msg, obj):
        parser   = SendTables(obj)
        delegate = RecordsMessages()

        parser.register(delegate) # for everything
        parser.parse()

        for capture in delegate.captures[SendTables.SendTable]:
            server_entity = ServerEntity(capture)
            self.server_entities.append(server_entity)
