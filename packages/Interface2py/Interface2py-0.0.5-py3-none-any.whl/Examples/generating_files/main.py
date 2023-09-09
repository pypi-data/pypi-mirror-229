#  you can also generate schema files based off of pre defined Interfaces

# to do this, use the jsonGen2 file 

# imports
import src.IF4 as IF4
import src.jsonGen2 as jsonGen2 

# first, you need to have an interface defined
# for this example, we will use a cookie interface

class Cookie(IF4.Interface):
    _properties = {
        "flavor": str,
        "whipped_cream": bool,
        "chocolate_sauce": bool,
        "size": str
    }



# the next step is to define the output path we want

pt = "output.json"


# finally, we can call the function

jsonGen2.genJson(pt, Cookie)

# this will output a json file like the one in the example folder