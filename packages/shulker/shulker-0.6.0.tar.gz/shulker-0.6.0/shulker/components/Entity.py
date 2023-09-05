import os
import json
import uuid
from typing import Union

from .NBT import NBT

path = os.path.dirname(os.path.abspath(__file__))
with open(f'{path}/../metadata/data/entity_nbt.json', 'r') as file:
    entities = json.load(file)

entities_nbt = {}
for key in entities:
    entities_nbt[key] = list(entities[key].keys())

def generate_signed_32bit_integer_uuid_list():
    # Generate a version 4 UUID
    uuid_v4 = uuid.uuid4()

    # Convert the UUID to a 128-bit integer
    uuid_int = uuid_v4.int

    # Create a list to store the 4 32-bit integers
    uuid_32bit_list = []

    # Mask and shift the 128-bit integer to obtain 4 32-bit integers
    for i in range(4):
        mask = 0xFFFFFFFF << (32 * i)
        uuid_32bit = (uuid_int & mask) >> (32 * i)

        # Convert the 32-bit unsigned integer to a signed integer
        if uuid_32bit >= 2**31:
            uuid_32bit -= 2**32

        uuid_32bit_list.append(uuid_32bit)

    return uuid_32bit_list[::-1]  # Reverse the list to get the correct order
   
class Entity:
    def __init__(self, name: str, nbt: Union[NBT, dict, None] = None):
        
        name = name.lower()
        
        if name not in entities.keys():
            raise ValueError(f"Entity '{name}' does not exist")
        
        self.__dict__['descriptor'] = name
        
        if type(nbt) == dict:
            self.__dict__['nbt'] = NBT(nbt)
        elif type(nbt) == NBT:
            self.__dict__['nbt'] = nbt
        elif nbt == None:
            self.__dict__['nbt'] = NBT()
        else:
            raise ValueError(f"nbt must be of type NBT or dict, not {type(nbt)}")

        self.__dict__['nbt'].UUID = generate_signed_32bit_integer_uuid_list()
        
    @property
    def attributes(self):
        return entities_nbt[self.descriptor]
    
    def update(self, nbt):
        from shulker.functions.update_entity import update
        
        uuid = self.__getattr__("UUID")
        return update(uuid, nbt)
    
    def summon(self, *args):
        from shulker.functions.default import summon
        
        if len(args) == 3:
            coords = (args[0], args[1], args[2])
        elif len(args) == 1:
            coords = args[0]
        else:
            raise ValueError(f"summon takes 1 (tuple, list, Coordinates...) or 3 (x, y, z) arguments, not {len(args)}")
        
        return summon(self, coords)
    
    def __setattr__(self, name, value):
        if name in self.attributes:
            self.nbt.__setattr__(name, value)
        else:
            raise ValueError(f"Attribute '{name}' for '{self.descriptor}' does not exist")

    def __getattr__(self, name):
        return getattr(self.nbt, name)
        
    def __str__(self):
        if hasattr(self, "nbt") and self.nbt not in [None, "", "{}"]:
            return f"{self.descriptor}{self.nbt}"
        else:
            return f"{self.descriptor}"

