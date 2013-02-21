from test import *

import skadi.demo as sd

class TestDemo(object):
    def test_parser_fires_all_delegates_by_default(self):
        delegate = RecordsCmds()

        demo_parser = demo_parser_for('12345678.dem')
        demo_parser.register(delegate)
        demo_parser.parse()

        assert len(delegate.recorded_cmds()) == 10

    def test_parser_fires_specified_delegate(self):
        delegate = RecordsCmds()
        mask     = sd.Demo.SendTables

        demo_parser = demo_parser_for('12345678.dem')
        demo_parser.register(delegate, mask)
        demo_parser.parse()

        assert len(delegate.recorded_cmds()) == 1

    def test_parser_fires_multiple_specified_delegates(self):
        delegate = RecordsCmds()
        mask     = sd.Demo.SignonPacket | sd.Demo.FileInfo

        demo_parser = demo_parser_for('12345678.dem')
        demo_parser.register(delegate, mask)
        demo_parser.parse()

        assert len(set(delegate.recorded_cmds())) == 2
