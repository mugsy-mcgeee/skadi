import types
import inspect
from collections import OrderedDict, defaultdict

import skadi.wex_impl as wex_impl
import skadi.wex_impl.trans as wex_trans

from skadi.engine import world

OFFSET_BASED = ['DT_DOTA_PlayerResource']
OFFSET_ARRAY_SIZE = 32


class valueOf(object):
  def __init__(self, prop_str):
    self.trans_func = lambda self,val,world:val

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

  def asWex(self, cls_str):
    # Assume the wex object is already created and populated,
    # we just need to find it's index and reference it
    pass

  def asString(self):
    self.trans_func = wex_trans.to_datatype

  def __call__(self, wex_obj, world):
    if wex_obj._offset_based:
      try:
        ehandle, offset = wex_obj.id
      except:
        raise Exception('Expected id tuple(ehandle,offset), not {}'.format(wex_obj.id))
      # offset based instances
      data_set = world.by_ehandle[ehandle]
      key = (self.prop_key, str(offset).zfill(4))
      try:
        return self.trans_func(self, data_set[key], world)
      except wex_trans.NotFound as e:
        print e
    else: 
      # object based instances
      prop_val = world.by_ehandle[wex_obj.id][self.prop_key]
      return self.trans_func(self, prop_val, world)


class Entity(object):
  def __init__(self, entity_str):
    self.entity_str = entity_str
    
  def ValueOf(self, prop_str):
    return Property(self, prop_str, lambda x,val,y:val)

  def DataTypeFor(self, prop_str):
    return Property(self, prop_str, wex_trans.to_datatype)

  def __call__(self, wex_obj, stream):
    # If entity_str is shortname, perform prefix search
    if not self.entity_str.startswith('DT_'):
      # try DT_DOTA_ first
      search_str = 'DT_DOTA_{}'.format(self.entity_str)
      ents = stream.world.find_all_by_dt(search_str).keys()
      if len(ents) == 0: 
        # try DT_ next
        search_str = 'DT_{}'.format(self.entity_str)
        ents = stream.world.find_all_by_dt(search_str).keys()
    else:
      ents = stream.world.find_all_by_dt(self.entity_str).keys()
    return ents


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
      if isinstance(func, valueOf):
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
  def get_all(cls):
    # find the instance of our own class in wex_pkgs
    obj = wex_impl.get_wex_inst(cls)

    ents = obj._find_my_entities()
    print '{} Found {} entities'.format(cls.src_table, len(ents))
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
