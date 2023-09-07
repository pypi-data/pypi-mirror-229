# coding=utf-8
import os
import sys
import unittest

dirname = os.path.dirname(os.path.abspath(__file__))
project = os.path.abspath(os.path.join(dirname, '..'))

if project not in sys.path:
    sys.path.insert(0, project)


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def main():
        return unittest.main()
