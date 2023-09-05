import unittest

from shulker.components.BlockCoordinates import BlockCoordinates
from shulker.components.BlockZone import BlockZone, BlockZoneWrongCoordsType


class TestCoordinates(unittest.TestCase):
    def test_zone_with_blockcoords(self):
        """Test if BlockZone works with BlockCoordinates instances for both positions."""
        coords1 = BlockCoordinates(0, 0, 0)
        coords2 = BlockCoordinates(10, 10, 10)
        zone = BlockZone(coords1, coords2)

        diff = str(zone)
        test = "0 0 0 10 10 10"
        self.assertEqual(diff, test)

    def test_zone_with_tuple(self):
        """Test if BlockZone works with tuples for both positions."""
        coords1 = (0, 0, 0)
        coords2 = (10, 10, 10)
        zone = BlockZone(coords1, coords2)

        diff = str(zone)
        test = "0 0 0 10 10 10"
        self.assertEqual(diff, test)

    def test_zone_mixed(self):
        """Test if BlockZone works with a mix of BlockCoordinates instance and tuple for positions."""
        coords1 = (0, 0, 0)
        coords2 = BlockCoordinates(10, 10, 10)
        zone = BlockZone(coords1, coords2)

        diff = str(zone)
        test = "0 0 0 10 10 10"
        self.assertEqual(diff, test)

    def test_zone_wrong_args(self):
        """Test if BlockZone raises ZoneWrongCoordsType when provided with invalid arguments."""
        zone = BlockZone("hello", 1)
        with self.assertRaises(BlockZoneWrongCoordsType):
            str(zone)

    def test_zone_with_negative_coords(self):
        """Test if BlockZone works with negative coordinates."""
        coords1 = BlockCoordinates(-5, 0, -5)
        coords2 = BlockCoordinates(5, 5, 5)
        zone = BlockZone(coords1, coords2)

        diff = str(zone)
        test = "-5 0 -5 5 5 5"
        self.assertEqual(diff, test)
        
    def test_zone_same_coordinates(self):
        """Test if BlockZone works with the same coordinates for both positions."""
        coords1 = BlockCoordinates(0, 0, 0)
        coords2 = BlockCoordinates(0, 0, 0)
        zone = BlockZone(coords1, coords2)

        diff = str(zone)
        test = "0 0 0 0 0 0"
        self.assertEqual(diff, test)

    def test_zone_larger_coords_in_pos1(self):
        """Test if BlockZone works with larger coordinates in position 1 than in position 2."""
        coords1 = BlockCoordinates(10, 10, 10)
        coords2 = BlockCoordinates(0, 0, 0)
        zone = BlockZone(coords1, coords2)

        diff = str(zone)
        test = "10 10 10 0 0 0"
        self.assertEqual(diff, test)

    def test_zone_float_coordinates_rounded(self):
        """Test if BlockZone rounds floating-point coordinates correctly."""
        coords1 = (0.5, 1.2, 0)
        coords2 = (10.8, 10.3, 10.1)
        zone = BlockZone(coords1, coords2)

        diff = str(zone)
        test = "0 1 0 11 10 10"
        self.assertEqual(diff, test)


    
if __name__ == "__main__":
    unittest.main()
