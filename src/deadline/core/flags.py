
# 7_code_translation/src/deadline/core/flags.py
"""
Object flags system - translated from ZIL FLAGS
"""

from enum import Flag, auto

class ObjectFlag(Flag):
    """
    Object flags - equivalent to ZIL FLAGS
    These determine object behaviors and properties
    """
    NONE = 0
    TAKEABLE = auto()      # Can be picked up (TAKEBIT)
    CONTAINER = auto()     # Can contain other objects (CONTBIT)
    OPEN = auto()          # Container is open (OPENBIT)
    LOCKED = auto()        # Container is locked (LOCKEDBIT)
    LIGHT = auto()         # Provides light (LIGHTBIT)
    READABLE = auto()      # Can be read (READBIT)
    WEARABLE = auto()      # Can be worn (WEARBIT)
    EDIBLE = auto()        # Can be eaten (FOODBIT)
    DRINKABLE = auto()     # Can be drunk (DRINKBIT)
    WEAPON = auto()        # Is a weapon (WEAPONBIT)
    TOOL = auto()          # Is a tool (TOOLBIT)
    VEHICLE = auto()       # Can be ridden/entered (VEHBIT)
    SURFACE = auto()       # Objects can be placed on it (SURFACEBIT)
    TRANSPARENT = auto()   # Can see through it (TRANSBIT)
    INVISIBLE = auto()     # Cannot be seen normally (INVISIBLE)
    VISITED = auto()       # Room has been visited (RLANDBIT)
    SACRED = auto()        # Cannot be dropped (SACREDBIT)
    FEMALE = auto()        # Character is female (FEMALEBIT)
    PLURAL = auto()        # Object is plural (PLURALBIT)
    NARTICLE = auto()      # No article needed (NARTICLEBIT)
    PROPER = auto()        # Proper noun (PROPERBIT)
    TOUCHABLE = auto()     # Can be touched (TOUCHBIT)
    PERSON = auto()        # Is a person/character (PERSONBIT)
    ON = auto()            # Device is on (ONBIT)
    EVIDENCE = auto()      # Is evidence (custom for Deadline)
    HIDDEN = auto()        # Not visible until found
    FIXED = auto()         # Cannot be moved
    SEARCHED = auto()      # Has been searched