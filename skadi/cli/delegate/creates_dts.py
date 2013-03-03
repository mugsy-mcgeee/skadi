from skadi.core.parser import Parser

from skadi.cli.delegate import RecordsMessages
from skadi.cli.model.dt import DT

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
