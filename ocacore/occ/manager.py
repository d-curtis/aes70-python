from typing import ClassVar, Final, Any
from ocacore.occ.root import OcaRoot
from ocacore.occ.types import *

class OcaManager(OcaRoot):
    local_id: ClassVar[int] = 3
    class_version: ClassVar[OcaClassVersionNumber] = OcaClassVersionNumber(2)
    
    @property
    def local_properties(self) -> dict[str, Any]:
        return {
            OcaPropertyID(def_level=2, property_index=1): self.class_id,
            OcaPropertyID(def_level=2, property_index=2): self.class_version            
        }
    

# = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - 

class OcaDeviceManager(OcaManager):
    local_id: ClassVar[int] = 1
    class_version: ClassVar[OcaClassVersionNumber] = OcaClassVersionNumber(2)
    model_guid: Final[OcaModelGUID]
    serial_number: Final[OcaString]
    model_description: Final[OcaModelDescription]
    device_name: Final[OcaString]
    oca_version: Final[OcaUint16]
    device_role: OcaString
    user_inventory_code: OcaString
    enabled: OcaBoolean
    state: OcaDeviceState
    busy: OcaBoolean
    reset_cause: OcaResetCause
    message: OcaString
    managers: OcaList[OcaManagerDescriptor]
    device_revision_id: OcaString
    
    @property
    def local_properties(self) -> dict[str, Any]:
        return {
            OcaPropertyID(def_level=3, property_index=1): self.class_id,
            OcaPropertyID(def_level=3, property_index=2): self.class_version,
            OcaPropertyID(def_level=3, property_index=3): self.model_guid,
            OcaPropertyID(def_level=3, property_index=4): self.serial_number,
            OcaPropertyID(def_level=3, property_index=5): self.model_description,
            OcaPropertyID(def_level=3, property_index=6): self.device_name,
            OcaPropertyID(def_level=3, property_index=7): self.oca_version,
            OcaPropertyID(def_level=3, property_index=8): self.device_role,
            OcaPropertyID(def_level=3, property_index=9): self.user_inventory_code,
            OcaPropertyID(def_level=3, property_index=10): self.enabled,
            OcaPropertyID(def_level=3, property_index=11): self.state,
            OcaPropertyID(def_level=3, property_index=12): self.busy,
            OcaPropertyID(def_level=3, property_index=13): self.reset_cause,
            OcaPropertyID(def_level=3, property_index=14): self.message,
            OcaPropertyID(def_level=3, property_index=15): self.managers,
            OcaPropertyID(def_level=3, property_index=16): self.device_revision_id
        }
