from functools import wraps
import src.IF4 as IF4

def manuval(cls, errorOpt):
    errorOpt = bool(errorOpt)
    # Save original __init__
    orig_init = cls.__init__

    @wraps(cls)
    def new_init(self, *args, **kwargs):
        # Set properties without calling original __init__
        for key, value in kwargs.items():
            setattr(self, key, value)
        return None

    # Add .validate() method  
    def validate(self):
        if errorOpt == False:
            return False
        elif errorOpt == True:
            return orig_init(self, **self.__dict__) 
        else:
            return "Invalid output method"

    cls.__init__ = new_init
    cls.validate = validate
    return cls

'''
example usage:

@manuval
class Person(IF4.Interface):
  _properties = {
    'name': str,
    'age': int
  }

p = Person(name=5, age='foo') # No validation

print(p.name) # 5
print(p.age) # foo

#p.validate() # Manually validate
# Raises TypeError
'''