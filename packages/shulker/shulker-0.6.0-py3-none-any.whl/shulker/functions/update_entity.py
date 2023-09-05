from typing import Union

from shulker.components.NBT import NBT
from shulker.components.TargetSelector import TargetSelector
import shulker.functions.base_functions

def meta_update(selector: TargetSelector, nbt: NBT) -> str:
    return f"data merge entity {selector} {nbt}"

def update(
    selector: Union[TargetSelector, str],
    nbt: Union[NBT, dict, str]
) -> str:
    """
    Updates an entity with nbt_data
    
    selector can either be a TargetSelector object or an UUID string gotten
    from the UUID nbt of an entity
    """
    
    shulker.functions.base_functions.check_output_channel()
        
    if type(nbt) is dict:
        nbt = NBT(nbt)
    elif type(nbt) is str:
        nbt = NBT(nbt)
    elif type(nbt) is not NBT:
        raise ValueError(f"nbt must be of type NBT, dict, or str, not {type(nbt)}")
    
    if type(selector) is str:
        selector = TargetSelector("e", {"nbt": f"{{UUID:{selector}}}", "limit": 1})
        
    cmd = meta_update(selector, nbt)
    
    status = shulker.functions.base_functions.post(cmd)
    
    return status