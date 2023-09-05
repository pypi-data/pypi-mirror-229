import unittest

from shulker.components.TargetSelector import TargetSelector
from shulker.components.TargetSelector import (
    IncorrectTargetSelectorIdentifier,
    IncorrectTargetSelectorArgumentsType,
    InvalidTargetSelectorArgumentKey,
)


class TestBlock(unittest.TestCase):
    def test_valid_identifier(self):
        """Test if valid identifiers are correctly processed."""
        ts = TargetSelector('p')
        self.assertEqual(str(ts), '@p[]')
        ts = TargetSelector('a')
        self.assertEqual(str(ts), '@a[]')
        ts = TargetSelector('r')
        self.assertEqual(str(ts), '@r[]')
        ts = TargetSelector('s')
        self.assertEqual(str(ts), '@s[]')
        ts = TargetSelector('e')
        self.assertEqual(str(ts), '@e[]')

    def test_invalid_identifier(self):
        """Test if invalid identifiers raise the proper exception."""
        with self.assertRaises(IncorrectTargetSelectorIdentifier):
            TargetSelector('invalid')

    def test_valid_arguments(self):
        """Test if valid arguments are correctly processed."""
        ts = TargetSelector('e', {'type': 'cow', 'limit': 1})
        self.assertEqual(str(ts), '@e[type=cow,limit=1]')

    def test_invalid_argument_type(self):
        """Test if invalid argument types raise the proper exception."""
        with self.assertRaises(IncorrectTargetSelectorArgumentsType):
            TargetSelector('e', "type=cow,limit=1")

    def test_invalid_argument_key(self):
        """Test if invalid argument keys raise the proper exception."""
        with self.assertRaises(InvalidTargetSelectorArgumentKey):
            ts = TargetSelector('e', {'invalid_key': 'value'})
            str(ts)

    def test_list_arguments(self):
        """Test if list arguments are correctly processed."""
        ts = TargetSelector('a', {'tag': ['has_tag', '!hasnt_tag']})
        self.assertEqual(str(ts), '@a[tag=has_tag,tag=!hasnt_tag]')

    def test_empty_arguments(self):
        """Test if empty arguments are correctly processed."""
        ts = TargetSelector('s')
        self.assertEqual(str(ts), '@s[]')

    def test_no_arguments(self):
        """Test if None arguments are correctly processed."""
        ts = TargetSelector('r', None)
        self.assertEqual(str(ts), '@r[]')


if __name__ == "__main__":
    unittest.main()
