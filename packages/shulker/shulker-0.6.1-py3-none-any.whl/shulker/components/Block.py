import os
import json

from .BlockState import BlockState
from .BlockCoordinates import BlockCoordinates
from .Coordinates import Coordinates
from .NBT import NBT

path = os.path.dirname(os.path.abspath(__file__))
with open(f'{path}/../metadata/data/block_list.json', 'r') as file:
    blocks_data = json.load(file)

blocks = {}
for key in blocks_data:
    if 'properties' in blocks_data[key]:
        blocks[key] = {}
        blocks[key]['properties'] = blocks_data[key]['properties']
        for states in blocks_data[key]['states']:
            if 'default' in states.keys():
                blocks[key]['default'] = states['properties']
    else:
        blocks[key] = {'properties': {}, 'default': {}}

class Block:
    """
    A single '<block>' argument looks like this:

        'stone'
        'minecraft:redstone_wire[power=15,north=up,south=side]'
        'minecraft:jukebox{RecordItem:{...}}'
        'minecraft:furnace[facing=north]{BurnTime:200}'

    The format of '<block>' parameters is 'namespaced_ID[block_states]{data_tags}', in which
    block states and data tags can be omitted when they are not needed.

        Namespaced ID is required (though if namespace isn't set it defaults to 'minecraft:').
            In the context of "conditions"/testing for blocks, it can also be the namespace ID
            of block tag with the prefix of '#', such as '#minecraft:planks'.

        Block states are inside '[]', comma-separated and must be properties/values supported
        by the blocks. They are optional.
            'minecraft:stone[doesntexist=purpleberry]' is a syntax error, because 'stone'
            doesn't have 'doesntexist'.
            'minecraft:redstone_wire[power=tuesday]' is a syntax error, because 'redstone_wire''s
            'power' is a number between 0 and 15.

        Data tags are inside '{}'. It's optional.

        In the context of "conditions"/testing for blocks, only the states provided are tested.
            If command tests 'redstone_wire[power=15]', it checks only power, but ignores other
            states such as north.

        In the context of setting blocks, any states provided are set, but anything omitted retain
        their default values, depending on the block.
            If command sets 'redstone_wire[power=15]', it is set 'power' to 15, but 'north' is a
            default value (in this case, set to 'none').
    """

    def __init__(self, id: str, blockstate: BlockState = None, nbt: NBT = None):

        if not isinstance(id, str) or id == "":
            raise ValueError("id must be a non empty string")

        if ":" in id:
            parsed = id.split(":")
            self.__dict__['namespace'] = parsed[0]
            self.__dict__['id'] = parsed[1]
        else:
            self.__dict__['namespace'] = "minecraft"
            self.__dict__['id'] = id.replace(" ", "_")
            
        self.__dict__['descriptor'] = self.__dict__['namespace'] + ":" + self.__dict__['id']
            
        if self.__dict__['namespace'] == "minecraft":
            if self.__dict__['descriptor'] not in blocks:
                raise ValueError(f"Unknown block ID: {id}")

        self.__dict__['coords'] = None
        
        if self.__dict__['namespace'] == "minecraft":
            self.__dict__['blockstate'] = (
                blockstate if isinstance(blockstate, BlockState) else BlockState(blocks[self.descriptor]['default'])
            )
        else:
            self.__dict__['blockstate'] = (
                blockstate if isinstance(blockstate, BlockState) else BlockState({})
            )
        self.__dict__['nbt'] = nbt if isinstance(nbt, NBT) else NBT(nbt)

    @property
    def attributes(self):
        return blocks[self.descriptor]['properties']
    
    def set(self, *args, handler=None):
        from shulker.functions.default import set_block
        if len(args) == 3:
            coords = (args[0], args[1], args[2])
        elif len(args) == 1:
            coords = args[0]
        else:
            raise ValueError(f"set takes 1 (tuple, list, Coordinates...) or 3 (x, y, z) arguments and eventually an handler=.., not {len(args)}")
        
        self.__dict__['coords'] = coords
        
        if handler:
            return set_block(coords, self, handler)
        else:
            return set_block(coords, self)
    
    def move(self, *args, handler=None, replace_by="air"):
        from shulker.functions.default import set_block
        if len(args) == 3:
            new_coords = (args[0], args[1], args[2])
        elif len(args) == 1:
            new_coords = args[0]
        else:
            raise ValueError(f"move takes 1 (tuple, list, Coordinates...) or 3 (x, y, z) arguments and eventually an handler=.. and replace_by=.., not {len(args)}")
        
        old_coords = self.__dict__['coords']
        self.__dict__['coords'] = new_coords
        
        if handler:
            set_block(old_coords, replace_by, handler)
            set_block(new_coords, self, handler)
        else:
            set_block(old_coords, replace_by)
            set_block(new_coords, self)
    
    def offset(self, x=0, y=0, z=0, handler=None, replace_by="air"):

        if type(self.__dict__['coords']) in [tuple, list]:
            to_offset = BlockCoordinates(*self.__dict__['coords'])
        elif type(self.__dict__['coords']) in [BlockCoordinates, Coordinates]:
            to_offset = self.__dict__['coords']
            
        new_coords = to_offset.offset(x=x, y=y, z=z)
        
        self.move(new_coords, handler=handler, replace_by=replace_by)
        
    def __setattr__(self, name, value):
        if name == "nbt":
            if type(value) == NBT:
                self.__dict__['nbt'] = value
            else:
                self.__dict__['nbt'] = NBT(value)
        elif name == "blockstate":
            if type(value) == BlockState:
                self.__dict__['blockstate'] = value
            else:
                self.__dict__['blockstate'] = BlockState(value)
        elif name in self.attributes and value in self.attributes[name]:
            setattr(self.blockstate, name, value)
        else:
            raise ValueError(f"BlockState '{name}={value}' for '{self.descriptor}' does not exist")
    
    def __getattr__(self, name):
        if name in self.attributes:
            return getattr(self.blockstate, name)
        else:
            return getattr(self, name)
    
    def __str__(self):
        return f"{self.descriptor}{self.blockstate}{self.nbt}"
