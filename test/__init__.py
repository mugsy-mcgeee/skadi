import os, sys

from skadi.core.demo import Demo

pwd  = os.path.dirname(__file__)
root = os.path.join(pwd, '..')

def demo_for(fixture):
    return Demo(demo_path_for(fixture))

def demo_path_for(name):
    return os.path.join(root, 'demos', name)

class CapturesMessages(object):
    def __init__(self):
        self._captures = {}

    def __call__(self, message, obj):
        if not message in self._captures:
            self._captures[message] = []
        self._captures[message].append(obj)

    def recorded_messages(self):
        return self._captures.keys()

class CapturesFirstMessage(object):
    def __init__(self):
        self._capture = None

    def __call__(self, message, obj):
        if self._capture is None:
            self._capture = (message, obj)
