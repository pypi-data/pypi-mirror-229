import unittest

from shulker.components.BlockState import (
    BlockState,
    UnexpectedBlockStatePropertyValueType,
)
from shulker.components.Block import Block


class TestBlock(unittest.TestCase):
    def test_blockstate_without_args(self):
        """Test creating an empty BlockState with no arguments."""
        bs = BlockState()

        self.assertEqual(str(bs), "[]")

    def test_blockstate_without_attrs(self):
        """Test BlockState string representation when no attributes are set."""
        b = Block("dirt")
        
        self.assertEqual(str(b.blockstate), "[]")

    def test_blockstate_without_args_passed_to_Block(self):
        """Test BlockState passed as an argument to the Block class without arguments."""
        bs = BlockState()
        b = Block("dirt", blockstate=bs)

        self.assertEqual(str(b.blockstate), "[]")

    def test_blockstate_without_args_attributed_to_Block(self):
        """Test BlockState attributed to the Block class without arguments."""
        bs = BlockState()
        b = Block("dirt")
        b.blockstate = bs

        self.assertEqual(str(b.blockstate), "[]")

    def test_blockstate_with_arg(self):
        """Test creating a BlockState with a single property."""
        bs = BlockState({"snowy": True})

        diff = str(bs)
        test = "[snowy=true]"
        self.assertEqual(diff, test)

    def test_blockstate_with_args(self):
        """Test creating a BlockState with multiple properties."""
        bs = BlockState({"snowy": True, "facing": "north"})

        diff = str(bs)
        test = "[facing=north,snowy=true]"
        self.assertEqual(diff, test)

    def test_blockstate_via_attr(self):
        """Test setting a single property via attribute assignment."""
        bs = BlockState()
        bs.snowy = True

        diff = str(bs)
        test = "[snowy=true]"
        self.assertEqual(diff, test)

    def test_blockstate_via_attrs(self):
        """Test setting multiple properties via attribute assignments."""
        bs = BlockState()
        bs.snowy = True
        bs.facing = "north"

        diff = str(bs)
        test = "[facing=north,snowy=true]"
        self.assertEqual(diff, test)

    def test_blockstate_with_arg_passed_to_Block(self):
        """Test passing a BlockState with a single property to the Block class."""
        bs = BlockState({"snowy": True})
        b = Block("dirt", blockstate=bs)

        diff = str(b.blockstate)
        test = "[snowy=true]"
        self.assertEqual(diff, test)

    def test_blockstate_with_args_passed_to_Block(self):
        """Test passing a BlockState with multiple properties to the Block class."""
        bs = BlockState({"snowy": True, "facing": "north"})
        b = Block("dirt", blockstate=bs)

        diff = str(b.blockstate)
        test = "[facing=north,snowy=true]"
        self.assertEqual(diff, test)

    def test_blockstate_via_attr_through_Block(self):
        """Test setting a single property through the Block class."""
        b = Block("dirt")
        b.blockstate.snowy = True

        diff = str(b.blockstate)
        test = "[snowy=true]"
        self.assertEqual(diff, test)

    def test_blockstate_via_attrs_through_Block(self):
        """Test setting multiple properties through the Block class."""
        b = Block("dirt")
        b.blockstate.snowy = True
        b.blockstate.facing = "north"

        diff = str(b.blockstate)
        test = "[facing=north,snowy=true]"
        self.assertEqual(diff, test)

    def test_blockstate_mixed_attrs_and_args_through_Block(self):
        """Test a combination of properties set via attributes and arguments through the Block class."""
        bs = BlockState({"snowy": True, "dancing": "well"})
        b = Block("dirt")
        b.blockstate = bs
        b.blockstate.facing = "north"

        diff = str(b.blockstate)
        test = "[dancing=well,facing=north,snowy=true]"
        self.assertEqual(diff, test)

    def test_blockstate_override_attr_through_Block(self):
        """Test overriding a property through the Block class."""
        bs = BlockState({"snowy": True})
        b = Block("dirt")
        b.blockstate = bs
        b.blockstate.snowy = False

        diff = str(b.blockstate)
        test = "[snowy=false]"
        self.assertEqual(diff, test)

    def test_blockstate_incorrect_argument_value_type(self):
        """Test BlockState with an incorrect value type for a property."""
        bs = BlockState({"snowy": ["test", "test1"]})

        with self.assertRaises(UnexpectedBlockStatePropertyValueType):
            str(bs)
            
    def test_blockstate_non_string_key(self):
        """Test BlockState with a non-string key in the input dictionary."""
        with self.assertRaises(ValueError):
            bs = BlockState({123: True})
