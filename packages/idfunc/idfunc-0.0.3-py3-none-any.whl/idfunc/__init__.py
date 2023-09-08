__version__ = "0.0.3"
from .core import ( 
    ISANY_SYNONYMS, isany, anyq, notnone, isthing, something, isanything,
    
    passable, 

    IDENTITY_SYNONYMS, identity,
    noc, echo, iden, idfn, nada, noop, nodo, same,
    nomod, idfunc, nocall, mirror, reflect, giveback, keepsame, donothing,    
    IdentityWarning,   
)

__all__ = [    
    # not none function
    'isany', *ISANY_SYNONYMS, 'ISANY_SYNONYMS',

    # similar function
    'passable',

    # core function
    'identity', *IDENTITY_SYNONYMS,  'IDENTITY_SYNONYMS',

    # exceptions
    'IdentityWarning',
]