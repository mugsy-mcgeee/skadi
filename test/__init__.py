import os, sys

import skadi.demo as sd
pwd  = os.path.dirname(__file__)
root = os.path.join(pwd, '..')

def demo_path_for(name):
    return os.path.join(root, 'demos', name)

def demo_parser_for(fixture):
    return sd.Demo(demo_path_for(fixture))

class RecordsCmds(object):
    def __init__(self):
        self.cmds = {}

    def __call__(self, cmd, obj):
        if not cmd in self.cmds:
            self.cmds[cmd] = []
        self.cmds[cmd].append(obj)

    def recorded_cmds(self):
        return self.cmds.keys()
