import json
from typing import Union

from nbtlib import parse_nbt, serialize_tag
from nbtlib import Compound, List, Int

class NBT:
    def __init__(self, compound: Union[dict, str, Compound] = "{}"):

        if compound in [None, "", "{}", {}]:
            nbt = None
        elif isinstance(compound, Compound):
            nbt = compound
        elif isinstance(compound, str):
            nbt = json.loads(compound)
        elif isinstance(compound, dict):
            nbt = Compound(compound)
        else:
            raise ValueError(f"Expected dict, str or Compound, got {type(compound)}")

        if nbt:
            for key, value in nbt.items():
                if isinstance(value, Compound):
                    setattr(self, key, NBT(value))
                else:
                    setattr(self, key, value)

    def __setattr__(self, name, value):
        if isinstance(value, NBT):
            super().__setattr__(name, value)
        else:
            nbt = parse_nbt(str({name: value}))
            for key in nbt:
                super().__setattr__(key, nbt[key])

    def __str__(self):
        """The 'list of int' hacky thing is to fix a
        missing 'I;' in the serialized NBT tag.
        That minecraft seems to require"""
        
        compound = Compound()
        
        is_list_of_int = []
        for key, value in vars(self).items():
            if isinstance(value, NBT):
                compound[key] = Compound(value.__dict__)
            else:
                if isinstance(value, list):
                    if all([isinstance(x, int) for x in value]):
                        is_list_of_int.append(key)
                compound[key] = value
        
        serialized = serialize_tag(compound, compact=True)
        
        for list_of_int in is_list_of_int:
            serialized = serialized.replace(f"{list_of_int}:[", f"{list_of_int}:[I;")
        
        return serialized