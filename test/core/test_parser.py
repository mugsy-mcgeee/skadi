from test import demo_for
from test import CapturesFirstMessage, CapturesMessages

from skadi.core.demo import Demo
from skadi.core.parser import Parser

class TestParser(object):
    def test_it_fires_all_delegates_by_default(self):
        demo_delegate = CapturesFirstMessage()
        mask          = Demo.SendTables

        demo_parser = demo_for('12345678.dem')
        demo_parser.register(demo_delegate, mask)
        demo_parser.parse()

        _, obj = demo_delegate.capture

        packet_delegate = CapturesMessages()
        mask            = Parser.SendTable

        packet_parser = Parser(obj)
        packet_parser.register(packet_delegate, mask)
        packet_parser.parse()

        assert len(packet_delegate.recorded_messages()) == 1
        assert packet_delegate.recorded_messages() == \
           [Parser.SendTable]
