# coding=utf-8
import time
import json
import unittest

from test_base import BaseTestCase

from tone import utils


class TestCase(BaseTestCase):

    def test_attrdict(self):
        from tone.utils.attrdict import attrdict
        data = attrdict()
        self.assertFalse(data)
        with self.assertRaises(AttributeError):
            data.key

        data.key = 1
        self.assertEqual(data.key, 1)

        self.assertEqual(json.dumps(data), '{"key": 1}')

    def test_defaultattrdict(self):
        from tone.utils.attrdict import defaultattrdict
        data = defaultattrdict()
        self.assertFalse(data)
        self.assertFalse(data.data)
        self.assertFalse(data.data.data.data)

        data.data.data.data = 1
        self.assertTrue(callable(data.items))
        self.assertTrue(callable(data.values))

        self.assertEqual(json.dumps(data), '{"data": {"data": {"data": 1}}}')

    def test_loads(self):
        from tone.utils.attrdict import attrdict

        data = {'key': 123}
        data = attrdict.loads(data)
        self.assertIsInstance(data, attrdict)
        self.assertEqual(data.key, 123)

        data = {
            'key': [
                {
                    'key': 123,
                },
                [
                    {
                        'key': 123,
                    },
                    1234
                ]
            ]
        }
        result = attrdict.loads(data)
        self.assertEqual(str(data), str(result))

        self.assertIsInstance(data, dict)
        self.assertNotIsInstance(data, attrdict)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result, attrdict)
        self.assertIsInstance(result.key, list)

        self.assertEqual(result.key[0].key, 123)

    def test_json_loads(self):
        json = '{"data":{"data":1},"datas":[{"data":1}]}'
        from tone.utils.attrdict import defaultattrdict
        from tone.utils.attrdict import attrdict

        data = attrdict.json_loads(json)
        self.assertTrue(data)
        self.assertIsInstance(data, attrdict)

        data = defaultattrdict.json_loads(json)
        self.assertTrue(data)
        self.assertIsInstance(data, defaultattrdict)

        json = '[{"data":1},{"data":1}]'
        data = defaultattrdict.json_loads(json)
        self.assertTrue(data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_performance(self):
        from tone.utils.attrdict import defaultattrdict
        from tone.utils.attrdict import attrdict
        count = 100000

        def test_dict():
            data = {}

            start = time.time()
            for _ in range(count):
                data['key'] = 1
                assert data['key'] == 1

            end = time.time()
            print('test dict', end - start)

        def test_attrdict():
            data = attrdict()
            start = time.time()
            for _ in range(count):
                data.key = 1
                assert data.key == 1

            end = time.time()
            print('test attrdict', end - start)

        def test_defaultattrdict_attr():
            data = defaultattrdict()
            start = time.time()
            for _ in range(count):
                data.key = 1
                assert data.key == 1

            end = time.time()
            print('test defaultattrdict attr', end - start)

        def test_defaultattrdict_item():
            data = defaultattrdict()
            start = time.time()
            for _ in range(count):
                data['key'] = 1
                assert data['key'] == 1

            end = time.time()
            print('test defaultattrdict item', end - start)

        test_dict()
        test_attrdict()
        test_defaultattrdict_attr()
        test_defaultattrdict_item()


if __name__ == '__main__':
    TestCase.main()
