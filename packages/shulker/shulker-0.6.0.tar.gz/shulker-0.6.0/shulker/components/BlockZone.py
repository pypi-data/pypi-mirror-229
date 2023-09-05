from typing import Union

from .BlockCoordinates import BlockCoordinates

class BlockZone:
    """
    Custom component that is a set of two BlockCoordinates(), representing an area
    """

    def __init__(
        self, pos1: Union[BlockCoordinates, tuple], pos2: Union[BlockCoordinates, tuple]
    ):

        if isinstance(pos1, tuple):
            self.pos1 = BlockCoordinates(*pos1)
        else:
            self.pos1 = pos1

        if isinstance(pos2, tuple):
            self.pos2 = BlockCoordinates(*pos2)
        else:
            self.pos2 = pos2

    def contains(self, coord: BlockCoordinates) -> bool:
        """
        Checks if the given BlockCoordinates is within the BlockZone.
        """
        if not isinstance(coord, BlockCoordinates):
            raise BlockZoneWrongCoordsType(
                "BlockZone contains method requires a BlockCoordinates instance as input"
            )

        min_x = min(self.pos1.x, self.pos2.x)
        max_x = max(self.pos1.x, self.pos2.x)
        min_y = min(self.pos1.y, self.pos2.y)
        max_y = max(self.pos1.y, self.pos2.y)
        min_z = min(self.pos1.z, self.pos2.z)
        max_z = max(self.pos1.z, self.pos2.z)

        return (min_x <= coord.x <= max_x) and (min_y <= coord.y <= max_y) and (min_z <= coord.z <= max_z)

    def set(self, block, handler="replace", filter=""):
        from shulker.functions.default import set_zone

        self.__dict__['block'] = block
        return set_zone(self, block, handler, filter)
    
    def move(self, zone, handler="replace", filter="", replace_by="air"):
        from shulker.functions.default import set_zone

        if 'block' not in self.__dict__:
            raise ValueError("BlockZone.move() requires a block to be set first (by .set())")
        
        old_zone = BlockZone(self.pos1, self.pos2)
        
        if type(zone) is not BlockZone:
            new_zone = BlockZone(zone)
        else:
            new_zone = zone
        
        self.pos1 = new_zone.pos1
        self.pos2 = new_zone.pos2
        
        set_zone(old_zone, replace_by, handler, filter)
        set_zone(self, self.__dict__['block'], handler, filter)
    
    def offset_place(self, x=0, y=0, z=0, handler='replace', filter="", replace_by="air"):
        new_zone = self.offset(x, y, z)
        self.move(new_zone, handler=handler, filter=filter, replace_by=replace_by)
    
    def offset(self, x=0, y=0, z=0):
        """
        Offsets the coordinates by the given tuple and returns a new Zone object.
        """
        return BlockZone(self.pos1.offset(x, y, z), self.pos2.offset(x, y, z))
        
    def __str__(self):
        if not isinstance(self.pos1, BlockCoordinates) or not isinstance(
            self.pos2, BlockCoordinates
        ):
            raise BlockZoneWrongCoordsType(
                "a BlockZone requires to be provided a set of two BlockCoordinates instances as pos1 and pos2"
            )

        return f"{self.pos1} {self.pos2}"


class BlockZoneWrongCoordsType(Exception):
    pass
