import unittest

from shulker.components.Coordinates import Coordinates, WrongCaretNotation

class TestCoordinates(unittest.TestCase):
    def test_init(self):
        """Checks if the Coordinates class initializes correctly."""
        
        coords = Coordinates(1, 2, 3)
        self.assertEqual(coords.x, 1)
        self.assertEqual(coords.y, 2)
        self.assertEqual(coords.z, 3)
        self.assertIsNone(coords.yaw)
        self.assertIsNone(coords.pitch)

    def test_init_with_yaw_and_pitch(self):
        """Checks if the Coordinates class initializes correctly."""
        
        coords = Coordinates(1, 2, 3, 90, 45)
        self.assertEqual(coords.x, 1)
        self.assertEqual(coords.y, 2)
        self.assertEqual(coords.z, 3)
        self.assertEqual(coords.yaw, 90)
        self.assertEqual(coords.pitch, 45)

    def test_check_carets_valid(self):
        """Verifies that check_carets() method works correctly."""
        
        coords = Coordinates("^1", "^2", "^3")
        try:
            coords.check_carets()
        except WrongCaretNotation:
            self.fail("check_carets() raised WrongCaretNotation unexpectedly")

    def test_check_carets_invalid(self):
        """Verifies that check_carets() method raises an exception."""
        
        coords = Coordinates(1, "^2", 3)
        with self.assertRaises(WrongCaretNotation):
            coords.check_carets()

    def test_offset_without_yaw_and_pitch(self):
        """Checks if offset() method correctly offsets the values."""
        
        coords = Coordinates(1, 2, 3)
        new_coords = coords.offset(1, 1, 1)
        self.assertEqual(new_coords.x, 2)
        self.assertEqual(new_coords.y, 3)
        self.assertEqual(new_coords.z, 4)
        self.assertIsNone(new_coords.yaw)
        self.assertIsNone(new_coords.pitch)

    def test_offset_with_yaw_and_pitch(self):
        """Checks if offset() method correctly offsets the values."""
        
        coords = Coordinates(1, 2, 3, 90, 45)
        new_coords = coords.offset(1, 1, 1, 10, 5)
        self.assertEqual(new_coords.x, 2)
        self.assertEqual(new_coords.y, 3)
        self.assertEqual(new_coords.z, 4)
        self.assertEqual(new_coords.yaw, 100)
        self.assertEqual(new_coords.pitch, 50)

    def test_str_without_yaw_and_pitch(self):
        """Verifies that __str__() method returns the correct string."""
        
        coords = Coordinates(1, 2, 3)
        self.assertEqual(str(coords), "1 2 3")

    def test_str_with_yaw_and_pitch(self):
        """Verifies that __str__() method returns the correct string."""
        
        coords = Coordinates(1, 2, 3, 90, 45)
        self.assertEqual(str(coords), "1 2 3 90 45")

    def test_str_with_caret_notation(self):
        """Verifies that __str__() method returns the correct string."""
        
        coords = Coordinates("^1", "^2", "^3")
        self.assertEqual(str(coords), "^1 ^2 ^3")

    def test_str_with_caret_notation_and_yaw_and_pitch(self):
        """Verifies that __str__() method returns the correct string."""
        
        coords = Coordinates("^1", "^2", "^3", 90, 45)
        self.assertEqual(str(coords), "^1 ^2 ^3 90 45")

    def test_init_with_floats(self):
        """Checks if Coordinates class initializes correctly with floats."""
        
        coords = Coordinates(1.5, 2.5, 3.5)
        self.assertEqual(coords.x, 1.5)
        self.assertEqual(coords.y, 2.5)
        self.assertEqual(coords.z, 3.5)

    def test_init_with_strings(self):
        """Checks if Coordinates class initializes correctly with strings."""
        
        coords = Coordinates("1", "2", "3")
        self.assertEqual(coords.x, "1")
        self.assertEqual(coords.y, "2")
        self.assertEqual(coords.z, "3")

    def test_init_with_mixed_types(self):
        """Checks if Coordinates class initializes correctly with mixed types."""
        
        coords = Coordinates("1", 2.5, 3)
        self.assertEqual(coords.x, "1")
        self.assertEqual(coords.y, 2.5)
        self.assertEqual(coords.z, 3)

    def test_offset_with_floats(self):
        """Checks if offset() method correctly offsets values with floats."""
        
        coords = Coordinates(1.5, 2.5, 3.5)
        new_coords = coords.offset(0.5, 0.5, 0.5)
        self.assertEqual(new_coords.x, 2)
        self.assertEqual(new_coords.y, 3)
        self.assertEqual(new_coords.z, 4)

    def test_str_with_floats(self):
        """Verifies that __str__() method returns the correct string with floats."""
        
        coords = Coordinates(1.5, 2.5, 3.5)
        self.assertEqual(str(coords), "1.5 2.5 3.5")

    def test_str_with_strings(self):
        """Verifies that __str__() method returns the correct string with strings."""
        
        coords = Coordinates("1", "2", "3")
        self.assertEqual(str(coords), "1 2 3")

    def test_str_with_mixed_types(self):
        """Verifies that __str__() method returns the correct string with mixed types."""
        
        coords = Coordinates("1", 2.5, 3)
        self.assertEqual(str(coords), "1 2.5 3")
    
    def test_init_with_negative_values(self):
        """Checks if Coordinates class initializes correctly with negative values."""
        
        coords = Coordinates(-1, -2, -3, -90, -45)
        self.assertEqual(coords.x, -1)
        self.assertEqual(coords.y, -2)
        self.assertEqual(coords.z, -3)
        self.assertEqual(coords.yaw, -90)
        self.assertEqual(coords.pitch, -45)

    def test_offset_with_negative_values(self):
        """Checks if offset() method correctly offsets values with negative values."""
        
        coords = Coordinates(1, 2, 3)
        new_coords = coords.offset(-1, -1, -1)
        self.assertEqual(new_coords.x, 0)
        self.assertEqual(new_coords.y, 1)
        self.assertEqual(new_coords.z, 2)

    def test_init_with_float_yaw_and_pitch(self):
        """Checks if Coordinates class initializes correctly with float yaw and pitch."""
        
        coords = Coordinates(1, 2, 3, 90.5, 45.5)
        self.assertEqual(coords.x, 1)
        self.assertEqual(coords.y, 2)
        self.assertEqual(coords.z, 3)
        self.assertEqual(coords.yaw, 90.5)
        self.assertEqual(coords.pitch, 45.5)

    def test_init_with_string_yaw_and_pitch(self):
        """Checks if Coordinates class initializes correctly with string yaw and pitch."""
        
        coords = Coordinates(1, 2, 3, "90", "45")
        self.assertEqual(coords.x, 1)
        self.assertEqual(coords.y, 2)
        self.assertEqual(coords.z, 3)
        self.assertEqual(coords.yaw, "90")
        self.assertEqual(coords.pitch, "45")

