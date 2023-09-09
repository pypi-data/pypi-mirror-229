#here is a basic example of using the Interface class

'''
MOVE THIS TO THE SAME LEVEL AS THE MAIN FILE!!
'''

import src.IF4 as IF4

#we will make an interface based off of Address

class Address(IF4.Interface):    #subclass the Interface class
    _properties = {              # add a properties 
        "street": str,
        "houseNumber": int,
        "mailbox": bool
    }


#to inialize an object:

address1 = Address(street="Main", houseNumber=123, mailbox=False)      # returns no error as this meets the typing set in the base interface

#to access a part, just do it as you would a normal class

street1 = address1.street

#interfaces typechecks at inialization, so if we were to try to create an object that didnt meet the expectations:

address2 = Address(street="Main", houseNumber="hi", mailbox=True)     # returns '''TypeError: Invalid type 'houseNumber': expected <class 'int'>'''

#to change a value, just do it as you would normally

address1.street = "Park Ave"

#if you have any questions/find any bugs PLEASE LEAVE AN ISSUE!!!



