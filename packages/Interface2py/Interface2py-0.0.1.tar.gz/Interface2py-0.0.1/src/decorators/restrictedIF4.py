from typing import Any
#import IF4
def restricted(**restrictions):

  def decorator(cls):

    # Save restrictions on class
    cls._restrictions = restrictions
    
    # Add validation method  
    @classmethod
    def _validate_restrictions(cls, kwargs):
      for key, allowed in cls._restrictions.items():
        if key in kwargs and kwargs[key] not in allowed:
          raise ValueError(f"{key} must be one of {allowed}")

    cls._validate_restrictions = _validate_restrictions
    
    # Override init
    orig_init = cls.__init__
    def __init__(self, *args, **kwargs):
      orig_init(self, *args, **kwargs)
      self._validate_restrictions(kwargs)

    cls.__init__ = __init__

    return cls

  return decorator
  
'''

EXAMPLE CODE:


@restricted(sentiment=["positive", "negative", "neutral"])
class SentimentAnalysis(IF4.Interface):
  _properties = {
    "sentiment": str
  }

good = SentimentAnalysis(sentiment="positive")   #works
bad = SentimentAnalysis(sentiment="bad") ##returns error
'''