from test import *

import skadi.demo as sd
import skadi.parser.send_tables as spst

class TestSendTablesParser(object):
    def test_parser_fires_all_delegates_by_default(self):
        demo_delegate = CapturesFirstMessage()
        mask          = sd.Demo.SendTables

        demo_parser = demo_parser_for('12345678.dem')
        demo_parser.register(demo_delegate, mask)
        demo_parser.parse()

        _, obj = demo_delegate.capture

        packet_delegate = CapturesMessages()
        mask            = spst.SendTables.SendTable

        packet_parser = spst.SendTables(obj)
        packet_parser.register(packet_delegate, mask)
        packet_parser.parse()

        assert len(packet_delegate.recorded_messages()) == 1
        assert packet_delegate.recorded_messages() == \
           [spst.SendTables.SendTable]
