# coding=utf-8
import unittest
import importlib


modules = [
    'test_utils_attrdict',
]


def main():
    suite = unittest.TestSuite()
    for name in modules:
        module = importlib.import_module(name)
        suite.addTest(unittest.makeSuite(module.TestCase))

    # failfast 如果失败则推出
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(suite)


if __name__ == '__main__':
    main()
