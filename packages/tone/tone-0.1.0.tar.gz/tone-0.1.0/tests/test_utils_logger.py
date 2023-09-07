# coding=utf-8
import sys
from io import StringIO

from test_base import BaseTestCase
import logging


class TestCase(BaseTestCase):

    def setUp(self):
        pass

    def test_logger(self):
        stderr = sys.stderr
        try:
            sys.stderr = StringIO()
            from tone import utils
            logger = utils.get_logger()
            logger.debug('hello world')
            self.assertTrue('hello world' in sys.stderr.getvalue())
        finally:
            sys.stderr = stderr


if __name__ == '__main__':
    TestCase.main()
