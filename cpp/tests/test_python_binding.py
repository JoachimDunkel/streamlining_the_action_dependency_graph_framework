import sys
import os
import unittest

sys.path.append(os.path.abspath('../build'))

import dependency_creator


class TestDependencyCreator(unittest.TestCase):
    def test_hello_from_cpp(self):
        result = dependency_creator.hello_from_cpp()
        self.assertEqual(result, "hello from cpp")

    def test_create_dependency(self):
        action_1 = dependency_creator.Action((1, 0), (2, 0), 1, 42, 99)
        action_2 = dependency_creator.Action((2, 0), (3, 0), 1, 66, 142)
        
        result = dependency_creator.create_type2_dependencies([action_1, action_2])
        expected = [(142, 99)]
        self.assertListEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
