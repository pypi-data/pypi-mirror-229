from typing import get_type_hints
#import src.IF4 as IF4

def immutable(cls):

  props = cls._properties

  for name in props:
     setattr(cls, f"_{name}", None)  

  def setter(self, name, value):
      raise AttributeError(f"Cannot modify immutable property {name}")

  def custom_setattr(self, name, value):
      if name in props:
          setter(self, name, value)
      else:
          cls.__dict__['__setattr__'](self, name, value)

  cls.__setattr__ = custom_setattr
  
  return cls

'''
example usage:


@immutable
class Person(IF4.Interface):
  _properties = {
        "name": str,
        "age": int
  }

p = Person(name="Hi", age=3)
p.name = "Test" # Raises exception
'''