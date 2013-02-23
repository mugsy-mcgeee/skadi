from test import demo_parser_for, \
                 CapturesFirstMessage, CapturesMessages

import skadi.core.demo as demo
import skadi.core.parser.send_tables as pst

class TestSendTablesParser(object):
    def test_parser_fires_all_delegates_by_default(self):
        demo_delegate = CapturesFirstMessage()
        mask          = demo.Demo.SendTables

        demo_parser = demo_parser_for('12345678.dem')
        demo_parser.register(demo_delegate, mask)
        demo_parser.parse()

        _, obj = demo_delegate.capture

        packet_delegate = CapturesMessages()
        mask            = pst.SendTables.SendTable

        packet_parser = pst.SendTables(obj)
        packet_parser.register(packet_delegate, mask)
        packet_parser.parse()

        assert len(packet_delegate.recorded_messages()) == 1
        assert packet_delegate.recorded_messages() == \
           [pst.SendTables.SendTable]
