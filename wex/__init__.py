import inspect
from collections import OrderedDict, defaultdict

import skadi.wex_impl as wex_impl
import skadi.wex_impl.trans as wex_trans
from skadi.wex_impl import ent_type

OFFSET_BASED = ['DT_DOTA_PlayerResource']


class Property(object):
  def __init__(self, ent_obj, prop_str, trans_func):
    self.ent_list = ent_obj
    self.trans_func = trans_func

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

  def __call__(self, wex_obj, stream):
    ents = self.ent_list(wex_obj, stream)

    values = {}
    if len(ents) > 0:
      if ent_type(stream, ents[0]) in OFFSET_BASED: 
        # offset based instances
        assert(len(ents) == 1)
        data_set = ents[0][2]
        keys = [k for k in data_set.keys() if k[0] == self.prop_key]
        for key in keys:
          offset = int(key[1])
          values[offset] = self.trans_func(self, data_set[key], stream)
      else: 
        # object based instances
        for i,e in enumerate(ents):
          prop_val = e[2][self.prop_key]
          values[i] = self.trans_func(self, prop_val, stream)

    return values


class Entity(object):
  def __init__(self, entity_str):
    self.entity_str = entity_str
    
  def ValueOf(self, prop_str):
    return Property(self, prop_str, lambda x,val,y:val)

  def DataTypeFor(self, prop_str):
    return Property(self, prop_str, wex_trans.to_datatype)

  def __call__(self, wex_obj, stream):
    all_ents = stream.entities.values()
    # If entity_str is shortname, perform prefix search
    if not self.entity_str.startswith('DT_'):
      # try DT_DOTA_ first
      search_str = 'DT_DOTA_{}'.format(self.entity_str)
      ents = filter(lambda e:ent_type(stream,e)==search_str, all_ents)
      if len(ents) == 0: 
        # try DT_ next
        search_str = 'DT_{}'.format(self.entity_str)
        ents = filter(lambda e:ent_type(stream,e)==search_str, all_ents)
    else:
      ents = filter(lambda e:ent_type(stream,e)==self.entity_str, all_ents)
    return ents

# Entity aliases
class From(Entity):
  pass


class Wex(object):
  def __init__(self):
    # META
    self._obj_list = {}

    # INSTANCE
    self._id = None
    self._data = {}
    self._prop_list = []
    for member in inspect.getmembers(self):
      name,func = member
      if isinstance(func, Property) or isinstance(func, Entity):
        self._prop_list.append( (name,func) )

  # META
  @classmethod
  def __iter__(cls):
    # find the instance of our own class in wex_pkgs
    obj = wex_impl.get_wex_inst(cls)
    # Return iter of all instances
    if obj is not None:
      return (x for x in obj._obj_list.values())
    else:
      return None

  # META
  @classmethod
  def get_all(cls):
    # find the instance of our own class in wex_pkgs
    obj = wex_impl.get_wex_inst(cls)
    # Return list of all instances
    if obj is not None:
      return obj._obj_list.values()
    else:
      return None

  #META
  def process(self, stream):
    # attempt to process 'id' first and only when we
    # instantiate the class for the first time. 
    # it is necessary that id cannot change
    for _,func in ((n,f) for (n,f) in self._prop_list if n == 'id'):
      for id in func(self, stream).itervalues():
        if id not in self._obj_list:
          self._obj_list[id] = self.__class__()
          self._obj_list[id]._data['id'] = id

    # process all properties except 'id'
    for name,func in ((n,f) for (n,f) in self._prop_list if n != 'id'):
      values = func(self, stream)
      for i,v in values.iteritems():
        if i not in self._obj_list:
          pass
          #self._obj_list[i] = self.__class__()
        else:
          self._obj_list[i]._data[name] = v

  # INSTANCE
  def __getattribute__(self, name):
    my_data = object.__getattribute__(self, '_data')
    if name in my_data:
      return my_data[name]
    else:
      return object.__getattribute__(self, name)
