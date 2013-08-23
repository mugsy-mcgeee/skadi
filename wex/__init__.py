import types
import inspect
from collections import OrderedDict, defaultdict

import skadi.wex_impl as wex_impl

from skadi.engine import world as se_world

OFFSET_BASED = ['DT_DOTA_PlayerResource']
OFFSET_ARRAY_SIZE = 32


class PropertyNotFound(Exception):
  pass
class WexNotFound(Exception):
  pass


class valueOf(object):
  def __init__(self, prop_str):
    self.trans_func = lambda wex_obj,self,val,world:val

    if len(prop_str.split()) == 2:
      self.prop_key = tuple(prop_str.split())
      if self.prop_key[1].startswith('m_h'):
        self.is_handle = True
      else:
        self.is_handle = False
    else:
      self.prop_key = prop_str
      if self.prop_key.startswith('m_h'):
        self.is_handle = True
      else:
        self.is_handle = False

  def asWex(self, wex_cls_str):
    def _func(wex_obj, prop_obj, src_val, world):
      other_wex = wex_impl.find_wex_class(wex_cls_str)
      if other_wex is not None:
        index,serial = se_world.from_ehandle(src_val)
        if index == 2047: # undefined object
          return None
        else:
          if len(other_wex._obj_list) == 0:
            print 'getall'
            other_wex.get_all() # call this to create objs if needed
          return other_wex._obj_list[src_val]
      else:
        obj_name = wex_obj.__class__.__name__
        msg = '{} not found as referenced in {}'.format(wex_cls_str, obj_name)
        raise WexNotFound(msg)

    self.trans_func = _func
    return self

  def __call__(self, wex_obj, world):
    if wex_obj._offset_based:
      try:
        ehandle, offset = wex_obj.id
      except:
        raise Exception('Expected id tuple(ehandle,offset), not {}'.format(wex_obj.id))
      # offset based instances
      data_set = world.by_ehandle[ehandle]
      key = (self.prop_key, str(offset).zfill(4))
      return self.trans_func(wex_obj, self, data_set[key], world)
    else: 
      # object based instances
      prop_val = world.by_ehandle[wex_obj.id][self.prop_key]
      return self.trans_func(wex_obj, self, prop_val, world)


class myDatatype(object):
  def __call__(self, wex_obj, world):
    if wex_obj._offset_based:
      try:
        ehandle, offset = wex_obj.id
      except:
        raise Exception('Expected id tuple(ehandle,offset), not {}'.format(wex_obj.id))
      return world.fetch_recv_table(ehandle).dt
    else:
      return world.fetch_recv_table(wex_obj.id).dt


class source(object):
  """ @source decorator """
  def __init__(self, type_str):
    self.type_str = type_str

  def __call__(self, cls):
    setattr(cls, 'src_table', self.type_str)
    return cls


class Wex(object):
  def __init__(self, ehandle=None, offset_based=False):
    # META
    self._obj_list = {}
    self._world = None
    self._offset_based = offset_based

    # INSTANCE
    self.id = ehandle
    self._props = {}
    for member in inspect.getmembers(self):
      name,func = member
      if isinstance(func, valueOf) or isinstance(func, myDatatype):
        self._props[name] = func

  # META
  def _find_my_entities(self):
    ents = []

    # If entity_str is shortname, perform prefix search
    if not self.src_table.startswith('DT_'):
      # try DT_DOTA_ first
      search_str = 'DT_DOTA_{}'.format(self.src_table)
      self._offset_based = search_str in OFFSET_BASED
      ents = self._world.find_all_by_dt(search_str).keys()
      if len(ents) == 0: 
        # try DT_ next
        search_str = 'DT_{}'.format(self.src_table)
        self._offset_based = search_str in OFFSET_BASED
        ents = self._world.find_all_by_dt(search_str).keys()
    else:
      ents = self._world.find_all_by_dt(self.src_table).keys()
      self._offset_based = self.src_table in OFFSET_BASED
    return ents

  # META
  @classmethod
  def all(cls):
    # find the instance of our own class in wex_pkgs
    obj = wex_impl.get_wex_inst(cls)

    ents = obj._find_my_entities()
    for ehandle in ents:
      if obj._offset_based:
        for offset in range(OFFSET_ARRAY_SIZE):
          key = '{}_{}'.format(ehandle, offset)
          if key not in obj._obj_list:
            print '\tInstantiating new OB {} = {}'.format(obj.__class__, key)
            obj._obj_list[key] = obj.__class__((ehandle,offset), obj._offset_based)
            obj._obj_list[key]._world = obj._world
      else:
        if ehandle not in obj._obj_list:
          print '\tInstantiating new EB {} = {}'.format(obj.__class__, ehandle, obj._world)
          obj._obj_list[ehandle] = obj.__class__(ehandle, obj._offset_based)
          obj._obj_list[ehandle]._world = obj._world

    return obj._obj_list.values()


  # INSTANCE
  def __getattribute__(self, name):
    _props = object.__getattribute__(self, '_props')

    if name in _props:
      func = _props[name]
      return func(self, object.__getattribute__(self, '_world'))
    else:
      return object.__getattribute__(self, name)
