from typing import Union


#import IF4

def multiple(cls):
  
  props = cls._properties
  
  for name, typ in props.items():
    if isinstance(typ, tuple):
      props[name] = Union[typ]
      
  cls._properties = props
  
  return cls

#from IF4 import Interface


''' example usage:

    @multiple
    class Test(Interface):

      _properties = {
        "name": (bool, int)
      }

    t = Test(name=5) # Valid since name can be str or int
'''
