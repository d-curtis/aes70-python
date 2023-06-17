from pydantic import BaseModel
from ocacore.occ.types import *
from ocacore.occ.root import *


class ControlledDevice(BaseModel):
    control_objects: dict[OcaONo, OcaRoot] = {}
    
    def __init__(self) -> None:
        super().__init__()
        # Standard const objects
        self.control_objects.update({
            OcaONo(0x1): OcaRoot(
                object_number=OcaONo(0x1),
                lockable=OcaBoolean(False),
                role=OcaString("(Local Model) Root Block")
            )
        })

