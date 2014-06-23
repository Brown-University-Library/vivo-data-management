
import os
import unittest

import json

#Directory where test data is stored.
DATA_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data'
)

def load(fname):
    with open(os.path.join(DATA_PATH, fname)) as f:
        return json.load(f)

class BTest(unittest.TestCase):
    def eq(self, v1, v2):
        self.assertEqual(v1, v2)