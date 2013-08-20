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


def get_wex_inst(cls_name):
  for pkg in wex_pkgs:
    if pkg.__class__ == cls_name:
      return pkg
  return None


def process(stream):
  for cls in wex_pkgs:
    #print '{}.{}'.format(cls, cls.process)
    cls.process(stream)  


MAX_EDICT_BITS = 11
def to_ehandle(index, serial):
  return (serial << MAX_EDICT_BITS) | index

def from_ehandle(ehandle):
  index = ehandle & ((1 << MAX_EDICT_BITS) - 1)
  serial = ehandle >> MAX_EDICT_BITS
  return index, serial
