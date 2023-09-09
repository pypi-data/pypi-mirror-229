import json
from IF4 import Interface, InterfaceMeta

def interface_to_schema(interface):

  schema = {interface.__name__: {}}

  for prop, typ in interface._properties.items():

    if isinstance(typ, InterfaceMeta): 
      # Nested interface
      nested = interface_to_schema(typ)
      schema[interface.__name__][prop] = list(nested.keys())[0]

    else:
      # Primitive type
      schema[interface.__name__][prop] = python_type_to_json(typ)

  return schema


def python_type_to_json(typ):

  if typ is str:
    return "str"
  elif typ is int: 
    return "int"
  elif typ is bool:
    return "bool"
  else:
    raise ValueError(f"Unsupported type: {typ}")


# Example interfaces

class Street(Interface):
  _properties = {
    "StreetName": str,
    "Num": int    
  }

class Address(Interface):
  _properties = { 
    "st": Street,
    "MailBox": bool
  }  

class Person(Interface):
  _properties = {
    "name": str,
    "age": int, 
    "address": Address
  }

def genJson(pt, ift):
    pt = str(pt)
    # Generate schema
    schema = interface_to_schema(ift) 
    print(schema)

    # Write schema to file
    with open(pt, 'w') as f:
        json.dump(schema, f, indent=2)


pt = "./jsons/schema2.json"
ift = Address 
