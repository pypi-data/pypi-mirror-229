import math
import re

from .Coordinates import Coordinates

class BlockCoordinates(Coordinates):
    """
    The position of a block is actually the coordinates of the point at the lower northwest corner
    of the block, that is, the integer coordinates obtained by rounding down the coordinates
    inside the block.

    In Minecraft, decimal coordinates usually needs to be converted into integer coordinates by rounding
    down, which is called the block position of the coordinate.
    """

    def round_coord(self, coord):
        if isinstance(coord, str) and "." in coord:
            coord = re.sub(r"([\^~])(\d+\.\d+)", lambda m: m.group(1) + str(round(float(m.group(2)))), coord)
        elif isinstance(coord, float):
            coord = round(coord)
        return coord

    def offset(self, x=0, y=0, z=0) -> "BlockCoordinates":
        """
        Offsets the coordinates by the given tuple and returns a new BlockCoordinates object.
        """
        
        return BlockCoordinates(self.x + x, self.y + y, self.z + z)
    
    def set(self, block, handler=None):
        from shulker.functions.default import set_block
        from .Block import Block
        
        self.__dict__['block'] = Block(block)
        
        if handler:
            return set_block(self, self.__dict__['block'], handler)
        else:
            return set_block(self, self.__dict__['block'])
        
    def __str__(self):

        self.check_carets()

        self.x = self.round_coord(self.x)
        self.y = self.round_coord(self.y)
        self.z = self.round_coord(self.z)

        return f"{self.x} {self.y} {self.z}"
