from typing import ClassVar, Any, Final, Optional
from pydantic import BaseModel
from collections import namedtuple

from ocacore.occ.types import *


#TODO OcaRoot, OcaWorker, OcaAgent, OcaManager

class Method(BaseModel):
    """
    The Method model outlines the signature of a remote OCA method.

    Args:
        method_id:  The combined `def_level` and `method_index` of this method
        kwargs:     Dict of each argument to the method - `{ name: type }`
        returns:    Method return type
    """
    method_id: OcaMethodID
    kwargs: Optional[dict[str, OCCBase]]
    response_type: Optional[type]
    

class OcaRoot(BaseModel):
    # Properties
    @classmethod
    def class_id(cls) -> OcaClassID:
        """
        Recurse through parent classes to the `OcaRoot`, creating an address from
        each class' `local_id` 
        """
        def build_id(cls: OcaRoot, fields: list[int] = []) -> list[int]:
            fields.insert(0, cls.local_id)
            if not isinstance(cls, OcaRoot):
                fields = build_id(cls.__bases__[0], fields)
            return fields
        
        return OcaClassID(fields=build_id(cls))

    @property
    def property_ids(self) -> dict[OcaPropertyID, Any]:
        def build_props(obj: OcaRoot, props: dict[OcaPropertyID, Any] = {}):
            props.update(self.local_properties)
            if not isinstance(obj, OcaRoot):
                props = build_props(obj.__bases__[0], props)
            return props

        return build_props(self)
    
    @property
    def methods(self) -> dict[OcaMethodID, Method]:
        def build_methods(obj: OcaRoot, enumerated_methods: dict[OcaMethodID, Method] = {}):
            for attr_name in dir(obj):
                if attr_name == "methods":
                    continue
                try:
                    if isinstance(attr := getattr(obj, attr_name), Method):
                        enumerated_methods[attr.method_id] = attr
                except AttributeError:
                    pass
                
            if not isinstance(obj, OcaRoot):
                enumerated_methods = build_methods(obj.__bases__[0], enumerated_methods)
            return enumerated_methods

        return build_methods(self)

    local_id: ClassVar[int] = 1
    class_version: ClassVar[OcaClassVersionNumber] = OcaClassVersionNumber(2)
    object_number: Final[OcaONo]
    lockable: Final[OcaBoolean]
    role: Final[OcaString]

    @property
    def local_properties(self) -> dict[OcaPropertyID, Any]:
        return  {
            OcaPropertyID(def_level=1, property_index=1): self.class_id,
            OcaPropertyID(def_level=1, property_index=2): self.class_version,
            OcaPropertyID(def_level=1, property_index=3): self.object_number,
            OcaPropertyID(def_level=1, property_index=4): self.lockable,
            OcaPropertyID(def_level=1, property_index=5): self.role                         
        }

    # Methods
    get_class_identification: ClassVar[Method] = Method(
        method_id=OcaMethodID(def_level=1, method_index=1),
        response_type=OcaClassIdentification
    )
    get_lockable: ClassVar[Method] = Method(
        method_id=OcaMethodID(def_level=1, method_index=2),
        response_type=OcaBoolean
    )
    lock_total: ClassVar[Method] = Method(
        method_id=OcaMethodID(def_level=1, method_index=3)
    )
    unlock: ClassVar[Method] = Method(
        method_id=OcaMethodID(def_level=1, method_index=4)
    )
    get_role: ClassVar[Method] = Method(
        method_id=OcaMethodID(def_level=1, method_index=5),
        response_type=OcaString
    )
    lock_readonly: ClassVar[Method] = Method(
        method_id=OcaMethodID(def_level=1, method_index=6)
    )
    