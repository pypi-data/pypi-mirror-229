__version__ = "0.0.2"
from .core import (
    register, register_synonyms, pollute_globals,
    isany, anyq, notnone, isthing, something, isanything,
    passable, identity,
    noc, echo, iden, idfn,
    nada, noop, nodo, same,
    nomod, idfunc, nocall, mirror,
    reflect, giveback, keepsame, donothing,
    IDENTITY_SYNONYMS,
    IdentityWarning,
    
)

__all__ = [
    # decorators
    'register', 'register_synonyms' 'pollute_globals',

    # not none function
    'isany', 'anyq', 'notnone', 'isthing', 'something', 'isanything',

    # similar function
    'passable',

    # core function
    'identity',

    # synonyms
    'noc', 'echo', 'iden', 'idfn', 
    'nada', 'noop', 'nodo', 'same',
    'nomod', 'idfunc', 'nocall', 'mirror',
    'reflect', 'giveback', 'keepsame', 'donothing',
    'IDENTITY_SYNONYMS',

    # exceptions
    'IdentityWarning',

]