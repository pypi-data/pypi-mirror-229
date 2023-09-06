from typing import Union

from .Coordinates import Coordinates
from .BlockCoordinates import BlockCoordinates

class Zone:
    """
    Custom component that is a set of two Coordinates(), representing an area
    """

    def __init__(
        self, pos1: Union[Coordinates, tuple], pos2: Union[Coordinates, tuple]
    ):

        if isinstance(pos1, tuple):
            self.pos1 = Coordinates(*pos1)
        else:
            self.pos1 = pos1

        if isinstance(pos2, tuple):
            self.pos2 = Coordinates(*pos2)
        else:
            self.pos2 = pos2

    def contains(self, coord: Coordinates) -> bool:
        """
        Checks if the given Coordinates is within the Zone.
        """
        if not isinstance(coord, Coordinates):
            raise ZoneWrongCoordsType(
                "Zone contains method requires a Coordinates instance as input"
            )

        min_x = min(self.pos1.x, self.pos2.x)
        max_x = max(self.pos1.x, self.pos2.x)
        min_y = min(self.pos1.y, self.pos2.y)
        max_y = max(self.pos1.y, self.pos2.y)
        min_z = min(self.pos1.z, self.pos2.z)
        max_z = max(self.pos1.z, self.pos2.z)

        return (min_x <= coord.x <= max_x) and (min_y <= coord.y <= max_y) and (min_z <= coord.z <= max_z)
    
    def offset(self, x=0, y=0, z=0):
        """
        Offsets the coordinates by the given tuple and returns a new Zone object.
        """
        return Zone(self.pos1.offset(x, y, z), self.pos2.offset(x, y, z))
        
    def __str__(self):
        if not isinstance(self.pos1, Coordinates) or not isinstance(
            self.pos2, Coordinates
        ):
            raise ZoneWrongCoordsType(
                "A Zone requires to be provided a set of two Coordinates instances as pos1 and pos2"
            )

        return f"{self.pos1} {self.pos2}"

class ZoneWrongCoordsType(Exception):
    pass
