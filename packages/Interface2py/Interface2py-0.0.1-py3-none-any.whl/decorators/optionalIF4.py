import IF4
from typing import Optional


def optional(cls):
    for key, typ in cls._properties.items():
        if key.endswith("?"):
            attr = key[:-1]
      
            # Set default to None  
            setattr(cls, attr, None) 

    cls._properties = {
        key[:-1] if key.endswith("?") else key: typ
        for key, typ in cls._properties.items()
    }
    
    return cls

'''
EXAMPLE USAGE


@optional
class Test(IF4.Interface):

  _properties = {
    "name?": str,
  }

# Name defaults to None  
test = Test()
print(test.name) # None
'''