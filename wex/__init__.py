import types
import inspect
from collections import OrderedDict, defaultdict
from copy import copy

import skadi.wex_impl as wex_impl

from skadi.engine import world as se_world

OFFSET_BASED = ['DT_DOTA_PlayerResource']
OFFSET_ARRAY_SIZE = 32


class PropertyNotFound(Exception):
  pass
class WexNotFound(Exception):
  pass


class AsWex(object):
  def __init__(self, wex_cls_str, chain=None):
    self.wex_cls_str = wex_cls_str
    self.chain = chain or []
    print '{}AsWex({}, chain={})'.format('\t'*len(self.chain), wex_cls_str, chain)

  def valueOf(self, prop_str):
    o_chain = self.chain
    o_chain.append(self)
    self.chain = []
    return valueOf(prop_str, o_chain)

  def var(self, var_name):
    o_chain = self.chain
    o_chain.append(self)
    self.chain = []
    return valueOf(var_name, o_chain, True)

  def __call__(self, ctx, world):
    print 'AsWex.call({}, ctx={}, chain={}'.format(self.wex_cls_str, ctx, self.chain)
    for i,_func in enumerate(self.chain):
      print '\t{}'.format(i),
      ctx = _func(ctx, world)
    prop_val = ctx
    try:
      print '\tprop_val={}'.format(world.fetch_recv_table(prop_val))
    except KeyError:
      print '\tprop_val=Undefined ehandle'

    other_wex = wex_impl.find_wex_class(self.wex_cls_str)
    if other_wex is not None:
      index,serial = se_world.from_ehandle(prop_val)
      if index == 2047: # undefined object
        return None
      else:
        if len(other_wex._obj_list) == 0:
          other_wex.all() # call this to create objs if needed
        return other_wex._obj_list[prop_val]
    else:
      obj_name = wex_obj.__class__.__name__
      msg = '{} not found as referenced in {}'.format(wex_cls_str, obj_name)
      raise WexNotFound(msg)


class valueOf(object):
  def __init__(self, prop_str, chain=None, var_access=False):
    self.chain = chain or []
    print '{}valueOf({}, chain={})'.format('\t'*len(self.chain), prop_str, chain)
    self.var_access = var_access
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
    o_chain = self.chain
    o_chain.append(self)
    self.chain = []
    return AsWex(wex_cls_str, o_chain)

  def __call__(self, ctx, world):
    print 'valueOf.call({}, ctx={}, chain={}'.format(self.prop_key, ctx, self.chain)
    for i,_func in enumerate(self.chain):
      print '\t{}'.format(i),
      ctx = _func(ctx, world)
    wex_obj = ctx
    print '\twex_obj={}'.format(wex_obj)

    if self.var_access:
      return getattr(wex_obj, self.prop_key)
    else:
      if wex_obj._offset_based:
        try:
          ehandle, offset = wex_obj.id
        except:
          raise Exception('Expected id tuple(ehandle,offset), not {}'.format(wex_obj.id))
        # offset based instances
        data_set = world.by_ehandle[ehandle]
        key = (self.prop_key, str(offset).zfill(4))
        return data_set[key]
      else: 
        # object based instances
        prop_val = world.by_ehandle[wex_obj.id][self.prop_key]
        return prop_val


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
      if isinstance(func, AsWex) or \
         isinstance(func, valueOf) or \
         isinstance(func, myDatatype):
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
            obj._obj_list[key] = obj.__class__((ehandle,offset), obj._offset_based)
            obj._obj_list[key]._world = obj._world
      else:
        if ehandle not in obj._obj_list:
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
