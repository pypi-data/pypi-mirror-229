#from IF4 import Interface


def defaultval(cls):

  props = cls._properties.copy()
  
  for name, typ in props.items():
    if isinstance(typ, tuple):
      default = typ[1]
      typ = typ[0]
      props[name] = (typ, default)

  cls._properties = props

  def __init__(self, **kwargs):
    for key, val in cls._properties.items():
      typ, default = val
      if key not in kwargs:
        kwargs[key] = default
        
    self.__dict__.update(kwargs)

  cls.__init__ = __init__

  return cls
  
'''
example usage:

@defaultval
class Default(Interface):

  _properties = {
    "name": (str, "David"),
    "age": (int, 0)
  }

d = Default()
print(d.name) # Prints "David"

'''

