import unittest

from shulker.components.Coordinates import Coordinates
from shulker.components.Zone import Zone, ZoneWrongCoordsType


class TestCoordinates(unittest.TestCase):
    def test_zone_with_coordinates(self):
        """Test if Zone works with Coordinates instances for both positions."""
        coords1 = Coordinates(0, 0, 0)
        coords2 = Coordinates(10, 10, 10)
        zone = Zone(coords1, coords2)

        diff = str(zone)
        test = "0 0 0 10 10 10"
        self.assertEqual(diff, test)

    def test_zone_with_tuple(self):
        """Test if Zone works with tuples for both positions."""
        coords1 = (0, 0, 0)
        coords2 = (10, 10, 10)
        zone = Zone(coords1, coords2)

        diff = str(zone)
        test = "0 0 0 10 10 10"
        self.assertEqual(diff, test)

    def test_zone_mixed(self):
        """Test if Zone works with a mix of Coordinates instance and tuple for positions."""
        coords1 = (0, 0, 0)
        coords2 = Coordinates(10, 10, 10)
        zone = Zone(coords1, coords2)

        diff = str(zone)
        test = "0 0 0 10 10 10"
        self.assertEqual(diff, test)

    def test_zone_wrong_args(self):
        """Test if Zone raises ZoneWrongCoordsType when provided with invalid arguments."""
        zone = Zone("hello", 1)
        with self.assertRaises(ZoneWrongCoordsType):
            str(zone)

    def test_zone_contains_true(self):
        """Test if Zone contains method returns True for a coordinate within the zone."""
        coords1 = Coordinates(0, 0, 0)
        coords2 = Coordinates(10, 10, 10)
        zone = Zone(coords1, coords2)
        test_coord = Coordinates(5, 5, 5)

        self.assertTrue(zone.contains(test_coord))

    def test_zone_contains_false(self):
        """Test if Zone contains method returns False for a coordinate outside the zone."""
        coords1 = Coordinates(0, 0, 0)
        coords2 = Coordinates(10, 10, 10)
        zone = Zone(coords1, coords2)
        test_coord = Coordinates(15, 15, 15)

        self.assertFalse(zone.contains(test_coord))

    def test_zone_contains_error(self):
        """Test if Zone contains method raises ZoneWrongCoordsType for non-Coordinates input."""
        coords1 = Coordinates(0, 0, 0)
        coords2 = Coordinates(10, 10, 10)
        zone = Zone(coords1, coords2)

        with self.assertRaises(ZoneWrongCoordsType):
            zone.contains("hello")

    
if __name__ == "__main__":
    unittest.main()
