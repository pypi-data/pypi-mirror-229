import unittest

from shulker.components.Block import Block
from shulker.components.BlockState import BlockState
from shulker.components.NBT import NBT


class TestBlock(unittest.TestCase):
    def test_block_namespace(self):
        """Test constructor with a valid non-minecraft namespace"""
        block = Block("mod:op_block")

        diff = str(block)
        test = "mod:op_block[]{}"
        self.assertEqual(diff, test)

    def test_block_double_blockstate(self):
        """Test constructor with a valid blockstate of 2 elements"""
        block = Block("bedrock")
        block.blockstate = BlockState({"facing": "north", "half": "top"})

        diff = str(block)
        test = "minecraft:bedrock[facing=north,half=top]{}"
        self.assertEqual(diff, test)

    def test_block_mixed(self):
        """Test constructor with a valid blockstate, and a valid NBT"""
        block = Block("bedrock")
        block.nbt = NBT({"Fire": 4, "Air": 0})
        block.blockstate = BlockState({"facing": "north", "half": "top"})

        diff = str(block)
        test = "minecraft:bedrock[facing=north,half=top]{Fire:4,Air:0}"
        self.assertEqual(diff, test)
            
    def test_constructor_valid_block_id(self):
        """Test constructor with a valid block ID."""
        block = Block("minecraft:stone")
        self.assertEqual(block.descriptor, "minecraft:stone")

    def test_constructor_invalid_block_id(self):
        """Test constructor with an invalid block ID."""
        with self.assertRaises(ValueError):
            Block("minecraft:non_existent_block")
            
        with self.assertRaises(ValueError):
            Block("")

    def test_constructor_default_namespace(self):
        """Test constructor with default namespace (no namespace provided)."""
        block = Block("stone")
        self.assertEqual(block.descriptor, "minecraft:stone")

    def test_constructor_blockstate(self):
        """Test constructor with a valid block state."""
        blockstate = BlockState({"facing": "north"})
        block = Block("minecraft:furnace", blockstate=blockstate)
        self.assertEqual(block.blockstate, blockstate)

    def test_constructor_nbt(self):
        """Test constructor with a valid NBT."""
        nbt = NBT({"BurnTime": 200})
        block = Block("minecraft:furnace", nbt=nbt)
        self.assertEqual(block.nbt, nbt)

    def test_set_blockstate(self):
        """Test setting block state."""
        block = Block("minecraft:furnace")
        block.facing = "north"
        self.assertEqual(block.facing, "north")

    def test_get_blockstate(self):
        """Test getting block state."""
        block = Block("minecraft:furnace")
        block.facing = "north"
        self.assertEqual(block.facing, "north")

    def test_invalid_blockstate(self):
        """Test setting an invalid block state."""
        block = Block("minecraft:furnace")
        with self.assertRaises(ValueError):
            block.invalid_state = "value"

    def test_str_representation(self):
        """Test string representation of a block."""
        with self.assertRaises(ValueError):
            Block("minecraft:furnace[facing=north]{BurnTime:200}")

if __name__ == "__main__":
    unittest.main()
