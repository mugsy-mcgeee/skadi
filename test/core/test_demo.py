from test import demo_for, CapturesMessages
from skadi.core.demo import Demo

class TestDemo(object):
    def test_parser_fires_all_delegates_by_default(self):
        delegate = CapturesMessages()

        demo_parser = demo_for('12345678.dem')
        demo_parser.register(delegate)
        demo_parser.parse()

        assert len(delegate.recorded_messages()) == 10

    def test_parser_fires_specified_delegate(self):
        delegate = CapturesMessages()
        mask     = Demo.SendTables

        demo_parser = demo_for('12345678.dem')
        demo_parser.register(delegate, mask)
        demo_parser.parse()

        assert len(delegate.recorded_messages()) == 1
        assert delegate.recorded_messages() == [Demo.SendTables]

    def test_parser_fires_multiple_specified_delegates(self):
        delegate = CapturesMessages()
        mask     = Demo.SignonPacket | Demo.FileInfo

        demo_parser = demo_for('12345678.dem')
        demo_parser.register(delegate, mask)
        demo_parser.parse()

        assert len(set(delegate.recorded_messages())) == 2
