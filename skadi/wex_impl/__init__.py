import imp
import inspect
import os.path
from glob import glob


wex_pkgs = []

def wex_files():
  cur_path = os.path.dirname(os.path.abspath(__file__))
  wex_dir = os.path.join(cur_path, '..', '..', 'wex')
  return [f for f in glob(os.path.join(wex_dir, '*.py')) if not f.endswith('__init__.py')]


def load_wex():
  global wex_pkgs
  wex_pkgs = []

  print 'Loading wex files'
  for filename in wex_files():
    mod_name = 'wex.{}'.format(os.path.basename(filename)[:-3])
    mod = imp.load_source(mod_name, filename)
    for name,cls in inspect.getmembers(mod, inspect.isclass):
      # Lists all classes in module namespace, we are only looking for
      # the classes declared IN this module
      if cls.__module__ == mod_name:
        print '\t{} -> {}'.format(mod_name, cls.__name__)
        wex_pkgs.append(cls()) # instantiate class


def get_wex_inst(cls):
  cls_str = '{}.{}'.format(cls.__module__, cls.__name__)

  for wex in wex_pkgs:
    wex_str = '{}.{}'.format(wex.__class__.__module__, wex.__class__.__name__)
    if wex_str == cls_str:
      return wex
  print '{} not found in wex_pkgs:\n'.format(cls_name)
  print 'wex_pkgs={}'.format(wex_pkgs)
  return None


def process(stream):
  for cls in wex_pkgs:
    cls._world = stream.world

