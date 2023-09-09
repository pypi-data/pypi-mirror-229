# 1. Interface class
'''
import builtins 

class InterfaceMeta(type):
    def __init__(cls, name, bases, attrs):
        cls._properties = {}
        for base in bases:
            cls._properties.update(getattr(base, "_properties", {}))
        cls._properties.update(attrs.get("_properties", {}))
        
class Interface(metaclass=InterfaceMeta):
    def __init__(self, **kwargs):
        self._validate_args(kwargs)
        self.__dict__.update(kwargs)
        
        def _validate_args(self, kwargs):

            for key, value in kwargs.items():  
                prop_type = self._properties.get(key)
            
                if prop_type is None:
                    raise TypeError(f"Invalid argument '{key}'")  
            
                if not isinstance(value, prop_type) and not isinstance(value, Interface):

                    raise TypeError(f"Invalid type '{key}'")
                    
# 2. Generation and loading

def get_type(type_str):
  if type_str in ("str", "int", "bool"):
    return getattr(builtins, type_str)
  else:
    return type(type_str, (object,), {})
  

import json

def generate_interfaces(schema):
    interfaces = {}
    for name, props in schema.items():
        interfaces[name] = create_interface(name, props)
    return interfaces
    
def create_interface(name, props):

  properties = {}
  
  for p_name, p_type in props.items():

    if p_type in interfaces:
      # Property is an interface
      properties[p_name] = interfaces[p_type] 

    else:
      # Normal property
      properties[p_name] = get_type(p_type)


  return type(name, (Interface,), {'_properties': properties})
    
def load_data(data, interfaces):
    if isinstance(value, dict):
        value = load_data(value, interfaces)
    loaded = {}    
    for key, values in data.items():
        Interface = interfaces[key]
        loaded[key] = Interface(**values)
    return loaded
        
# Usage:

schema = json.load(open("./jsons/schema.json"))
interfaces = generate_interfaces(schema)

data = json.load(open("./jsons/inputData.json")) 
objects = load_data(data, interfaces)'''
from typing import Any
import json
import builtins

# Interface class

class InterfaceMeta(type):
    def __init__(cls, name, bases, attrs):
        cls._properties = {}
        for base in bases:
            cls._properties.update(getattr(base, "_properties", {}))
        cls._properties.update(attrs.get("_properties", {}))
        
class Interface(metaclass=InterfaceMeta):
    def __init__(self, **kwargs):
        self._validate_args(kwargs)
        self.__dict__.update(kwargs)
        
    def _validate_args(self, kwargs):
        for key, value in kwargs.items():
            prop_type = self._properties.get(key)
            if prop_type is None:
                raise TypeError(f"Invalid argument '{key}'")
                
            if not isinstance(value, prop_type) and not isinstance(value, Interface):
                raise TypeError(f"Invalid type '{key}': expected {prop_type}")
                

# Schema parsing

def get_type(type_str):
  if type_str in ("str", "int", "bool"):
    return getattr(builtins, type_str)
  else:
    return type(type_str, (object,), {})

def generate_interfaces(schema):
  interfaces = {}
  
  for name, props in schema.items():
    interfaces[name] = create_interface(name, props, interfaces)
  
  return interfaces

def create_interface(name, props, interfaces):
  properties = {}
  
  for p_name, p_type in props.items():
    if p_type in interfaces:
      properties[p_name] = interfaces[p_type]
    else:
      properties[p_name] = get_type(p_type)
      
  return type(name, (Interface,), {'_properties': properties})
  

# Loading data

def load_data(data, interfaces):

  loaded = {}

  for key, values in data.items():

    # Replace interface strings with instances
    for name, value in values.items():
      if isinstance(value, str) and value in interfaces:
        Interface = interfaces[value]
        values[name] = Interface()

    # Create interface instance  
    Interface = interfaces[key]
    obj = Interface(**values)
    loaded[key] = obj

    # Load nested objects
    for name, value in values.items():
      if isinstance(value, dict):
        loaded[name] = load_data(value, interfaces)

  return loaded
  
def getKeys(jsn):
  jsn = str(jsn)
  with open(jsn) as f:
    data = json.load(f)

  keys = list(data.keys())
  return keys 

# Usage

'''
example code:


schema = json.load(open("./jsons/schema.json"))
interfaces = generate_interfaces(schema)

data = json.load(open("./jsons/inputData.json"))
objects = load_data(data, interfaces)

print(objects)
'''

def getObjs(schema, data):
  schema = str(schema)
  data = str(data)


  schema = json.load(open(schema))
  interfaces = generate_interfaces(schema)

  data = json.load(open(data))
  objects = load_data(data, interfaces)

  return objects