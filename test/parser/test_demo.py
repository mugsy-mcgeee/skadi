from test import *

import skadi.parser.demo as sp

class Callback(object):
    def __init__(self):
        self.messages = []

    def __call__(self, message, message_data, context):
        self.messages.append(message)

class TestDemo(object):
    def setup(self):
        self.parser   = sp.Demo(demo_path_for('12345678.dem'))
        self.callback = Callback()

    def test_parser_fires_all_callbacks_by_default(self):
        self.parser.subscribe(self.callback)
        self.parser.parse()

        # 10 distinct message types parsed (in this fixture)
        messages = self.callback.messages
        assert len(set(messages)) == 10

    def test_parser_fires_specified_callback(self):
        self.parser.subscribe(self.callback, sp.Demo.Packet)
        self.parser.parse()

        # 1 distinct message type parsed
        messages = self.callback.messages
        assert messages.count(messages[0]) == len(messages)

    def test_parser_fires_multiple_specified_callbacks(self):
        mask = sp.Demo.SignonPacket | sp.Demo.FileInfo
        self.parser.subscribe(self.callback, mask)
        self.parser.parse()

        # 2 distinct message types parsed
        messages = self.callback.messages
        assert len(set(messages)) == 2