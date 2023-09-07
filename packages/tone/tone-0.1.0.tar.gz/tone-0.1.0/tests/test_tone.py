# coding=utf-8
import time
import json
import unittest

from test_base import BaseTestCase


class TestCase(BaseTestCase):

    def test_utils(self):
        import tone
        utils = tone.utils
        return utils

if __name__ == '__main__':
    TestCase.main()
