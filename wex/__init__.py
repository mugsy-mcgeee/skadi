import inspect
from collections import OrderedDict, defaultdict

import skadi.wex_impl as wex_impl


class Property(object):
  def __init__(self, ent_obj, prop_str):
    self.ent_list = ent_obj
    self.prop_str = prop_str
    self._as_dt = False

  def as_dt(self):
    self._as_dt = True
    return self

  def __call__(self, wex_obj, stream):
    ents = self.ent_list(wex_obj, stream)

    values = []
    for e in ents:
      prop_val = e[2][tuple(self.prop_str.split())]
      if self.prop_str.split()[1].startswith('m_h'): # handle 
        prop_val = wex_impl.from_ehandle(prop_val)[0]
      if self._as_dt:
        if prop_val != 2047:
          index = str(stream.entities[prop_val][0])
          prop_val = stream.recv_tables[index].dt
        else:
          prop_val = 'Undefined'
      values.append(prop_val)

    return values


class Entity(object):
  def __init__(self, entity_str):
    self.entity_str = entity_str
    
  def prop(self, prop_str):
    return Property(self, prop_str)

  def __call__(self, wex_obj, stream):
    all_ents = stream.entities.values()
    return filter(lambda e: stream.recv_tables[e[0]].dt==self.entity_str, all_ents)


class Wex(object):
  def __init__(self):
    # META
    self._obj_list = OrderedDict()

    # INSTANCE
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
    for name,func in self._prop_list:
      values = func(self, stream)
      for i,v in enumerate(values):
        if i not in self._obj_list:
          self._obj_list[i] = self.__class__()
        inst = self._obj_list[i]
        inst._data[name] = v

  # INSTANCE
  def __getattribute__(self, name):
    my_data = object.__getattribute__(self, '_data')
    if name in my_data:
      return my_data[name]
    else:
      return object.__getattribute__(self, name)
