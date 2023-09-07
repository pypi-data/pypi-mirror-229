# coding=utf-8
import time
import json
import unittest

from test_base import BaseTestCase

from tone import utils
import torch.nn as nn


class Model(nn.Module):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.model = nn.Sequential(
            nn.Linear(16, 32),
            nn.Linear(32, 1),
        )


class TestCase(BaseTestCase):

    def test_metrics(self):
        from tone.utils.learning import metrics
        import numpy as np

        real = np.linspace(0, 10, 100)
        pred = real + np.random.randn(real.shape[0]) * 0.01
        scores = metrics(real, pred)

    def test_ignore_warning(self):
        import tone
        import warnings
        tone.utils.learning.ignore_warning()
        warnings.warn("test warning..")

    def test_save_load_module(self):
        import os
        from tone.utils import learning

        model = Model()
        filename = './test_model.pt'
        learning.save_module(model, filename)
        model = learning.load_module(filename)
        self.assertEqual(type(model), Model)
        os.remove(filename)

    def test_save_load_pickle(self):
        import os
        from tone.utils import learning

        model = Model()
        filename = './test_model.pt'
        learning.save_pickle(model, filename)
        model = learning.load_pickle(filename)
        self.assertEqual(type(model), Model)
        os.remove(filename)


if __name__ == '__main__':
    TestCase.main()
