import unittest
import src
from src.command_processor import CommandProcessor

class TestCommandProcessor(unittest.TestCase):

    def test_process_returns_dict(self):
        return_dict = CommandProcessor('test/test_data.txt').process()
        self.assertIsInstance(return_dict, dict)

if __name__ == '__main__':
        unittest.main()