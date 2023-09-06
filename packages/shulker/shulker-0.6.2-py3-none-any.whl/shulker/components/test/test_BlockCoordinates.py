import unittest

from shulker.components.Coordinates import WrongCaretNotation
from shulker.components.BlockCoordinates import BlockCoordinates


class TestCoordinates(unittest.TestCase):
    def test_blockcoords_zeros(self):
        """Test that initializing BlockCoordinates with all zeros produces the expected output."""
        coords = BlockCoordinates(0, 0, 0)

        diff = str(coords)
        test = "0 0 0"
        self.assertEqual(diff, test)

    def test_coords_tilde(self):
        """Test that initializing BlockCoordinates with all tildes produces the expected output."""
        coords = BlockCoordinates("~", "~", "~")

        diff = str(coords)
        test = "~ ~ ~"
        self.assertEqual(diff, test)

    def test_coords_tilde_mixed(self):
        """Test that initializing BlockCoordinates with a mix of tildes and numbers produces the expected output."""
        coords = BlockCoordinates("~5", 0, "~-10")

        diff = str(coords)
        test = "~5 0 ~-10"
        self.assertEqual(diff, test)

    def test_coords_caret(self):
        """Test that initializing BlockCoordinates with all carets produces the expected output."""
        coords = BlockCoordinates("^", "^", "^")

        diff = str(coords)
        test = "^ ^ ^"
        self.assertEqual(diff, test)

    def test_coords_caret_mixed(self):
        """Test that initializing BlockCoordinates with a mix of carets and numbers produces the expected output."""
        coords = BlockCoordinates("^5", "^-10", "^")

        diff = str(coords)
        test = "^5 ^-10 ^"
        self.assertEqual(diff, test)

    def test_coords_caret_wrong(self):
        """Test that initializing BlockCoordinates with an incorrect caret notation raises the expected exception."""
        coords = BlockCoordinates(5, "^", "^")

        with self.assertRaises(WrongCaretNotation):
            str(coords)

    def test_coords_floats(self):
        """Test that initializing BlockCoordinates with floats and mixed notations produces the expected output."""
        coords = BlockCoordinates(1.5, "~0.1", 1)

        diff = str(coords)
        test = "2 ~0 1"
        self.assertEqual(diff, test)

    def test_blockcoords_offset(self):
        """Test that the offset method of BlockCoordinates produces the expected output."""
        coords = BlockCoordinates(1, 2, 3)
        offset_coords = coords.offset(1, 1, 1)
        
        diff = str(offset_coords)
        test = "2 3 4"
        self.assertEqual(diff, test)
    
if __name__ == "__main__":
    unittest.main()
