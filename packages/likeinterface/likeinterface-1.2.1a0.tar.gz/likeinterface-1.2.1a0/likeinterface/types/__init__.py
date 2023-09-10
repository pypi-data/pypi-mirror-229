from typing import List, Literal, Optional, Union

from .auth import Authorization, User
from .balance import Balance
from .base import LikeObject, MutableLikeObject
from .file import File
from .like import Hand

__all__ = (
    "Authorization",
    "Balance",
    "File",
    "Hand",
    "LikeObject",
    "MutableLikeObject",
    "User",
)

for _entity_name in __all__:
    _entity = globals()[_entity_name]
    if not hasattr(_entity, "model_rebuild"):
        continue
    _entity.model_rebuild(
        _types_namespace={
            "List": List,
            "Optional": Optional,
            "Union": Union,
            "Literal": Literal,
            **{k: v for k, v in globals().items() if k in __all__},
        }
    )

del _entity
del _entity_name
