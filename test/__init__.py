import os, sys

pwd  = os.path.dirname(__file__)
root = os.path.join(pwd, '..')

def demo_path_for(name):
    return os.path.join(root, 'demos', name)
