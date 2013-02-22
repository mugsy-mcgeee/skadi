import os, sys

import skadi.demo as sd
pwd  = os.path.dirname(__file__)
root = os.path.join(pwd, '..')

def demo_path_for(name):
    return os.path.join(root, 'demos', name)

def demo_parser_for(fixture):
    return sd.Demo(demo_path_for(fixture))

class CapturesMessages(object):
    def __init__(self):
        self.captures = {}

    def __call__(self, message, obj):
        if not message in self.captures:
            self.captures[message] = []
        self.captures[message].append(obj)

    def recorded_messages(self):
        return self.captures.keys()

class CapturesFirstMessage(object):
    def __init__(self):
        self.capture = None

    def __call__(self, message, obj):
        if self.capture is None:
            self.capture = (message, obj)
