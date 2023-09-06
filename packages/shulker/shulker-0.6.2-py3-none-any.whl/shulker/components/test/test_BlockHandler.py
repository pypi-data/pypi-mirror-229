import unittest

from shulker.components.BlockHandler import BlockHandler, BlockHandlerWrongType
from shulker.components.Block import Block


class TestBlockHandler(unittest.TestCase):
    def test_handler_destroy(self):
        """Test if the destroy option is properly set and returned."""
        bh = BlockHandler("destroy")

        diff = str(bh)
        test = "destroy"
        self.assertEqual(diff, test)

    def test_handler_replace(self):
        """Test if the replace option is properly set and returned."""
        bh = BlockHandler("replace")

        diff = str(bh)
        test = "replace"
        self.assertEqual(diff, test)

    def test_handler_keep(self):
        """Test if the keep option is properly set and returned."""
        bh = BlockHandler("keep")

        diff = str(bh)
        test = "keep"
        self.assertEqual(diff, test)

    def test_handler_hollow(self):
        """Test if the hollow option is properly set and returned."""
        bh = BlockHandler("hollow")

        diff = str(bh)
        test = "hollow"
        self.assertEqual(diff, test)

    def test_handler_outline(self):
        """Test if the outline option is properly set and returned."""
        bh = BlockHandler("outline")

        diff = str(bh)
        test = "outline"
        self.assertEqual(diff, test)

    def test_handler_default(self):
        """Test if the default option (replace) is properly set and returned."""
        bh = BlockHandler()

        diff = str(bh)
        test = "replace"
        self.assertEqual(diff, test)

    def test_abritrary_handler(self):
        """Test if an arbitrary option raises the BlockHandlerWrongType exception."""
        with self.assertRaises(BlockHandlerWrongType):
            BlockHandler("imaginary")

    def test_wrong_handler_type(self):
        """Test if an incorrect option type (non-string) raises the BlockHandlerWrongType exception."""
        with self.assertRaises(BlockHandlerWrongType):
            BlockHandler(1)


if __name__ == "__main__":
    unittest.main()
