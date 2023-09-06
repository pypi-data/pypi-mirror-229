import unittest

from nbtlib import serialize_tag

from shulker.components.Entity import Entity, NBT, entities_nbt

class TestEntity(unittest.TestCase):

    def test_invalid_entity(self):
        """Test Entity class raises ValueError with invalid entity name."""
        with self.assertRaises(ValueError):
            Entity("invalid_entity")

    def test_valid_entity(self):
        """Test Entity class creates a valid instance with a valid entity name."""
        entity = Entity("Zombie")
        self.assertEqual(entity.descriptor, "zombie")

    def test_nbt_type(self):
        """Test Entity class raises ValueError with invalid nbt input type."""
        with self.assertRaises(ValueError):
            Entity("zombie", nbt="invalid_nbt_type")

    def test_valid_nbt(self):
        """Test Entity class creates a valid instance with a valid NBT object input."""
        entity = Entity("zombie", nbt=NBT({"CustomName": "zombie1"}))
        self.assertEqual(serialize_tag(entity.CustomName, compact=True), '"zombie1"')

    def test_dict_nbt(self):
        """Test Entity class creates a valid instance with a valid dictionary input for nbt."""
        entity = Entity("zombie", nbt={"CustomName": "zombie2"})
        self.assertEqual(serialize_tag(entity.CustomName, compact=True), '"zombie2"')

    def test_set_nonexistent_attribute(self):
        """Test Entity class raises ValueError when trying to set a nonexistent attribute to an instance."""
        entity = Entity("zombie")
        with self.assertRaises(ValueError):
            entity.invalid_attribute = "value"

    def test_set_valid_attribute(self):
        """Test Entity class sets a valid attribute for an instance."""
        entity = Entity("zombie")
        entity.Health = 20
        self.assertEqual(serialize_tag(entity.Health, compact=True), '20')

    def test_uuid_creation(self):
        """Test Entity class generates a UUID for each instance."""
        import re
        entity = Entity("zombie")
        uuid_str = entity.UUID
        uuid_list = [int(num) for num in re.findall(r'-?\d+', serialize_tag(uuid_str, compact=True))]
        self.assertEqual(len(uuid_list), 4)
        for i in uuid_list:
            self.assertTrue(isinstance(i, int))

    def test_str_representation(self):
        """Test __str__ method of the Entity class returns a string representation of the entity."""
        entity = Entity("zombie")
        self.assertTrue(isinstance(entity.__str__(), str))

    def test_attributes_property(self):
        """Test Entity class returns expected attributes for an entity."""
        entity = Entity("zombie")
        expected_attributes = entities_nbt["zombie"]
        self.assertEqual(entity.attributes, expected_attributes)

