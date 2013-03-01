from skadi.core.parser import Parser

from skadi.cli.delegate import RecordsMessages
from skadi.cli.model.server_entity import ServerEntity

class CreatesServerEntities(object):
    def __init__(self):
        self.server_entities = []

    def __call__(self, msg, obj):
        parser   = Parser(obj)
        delegate = RecordsMessages()

        parser.register(delegate) # for everything
        parser.parse()

        for capture in delegate.captures[Parser.SendTable]:
            server_entity = ServerEntity(capture)
            self.server_entities.append(server_entity)
