import pytest
from code_analysis.example.sample_code import *

def test_add():
    objct = add(1, 8)
    assert objct is not None  # Basic check

class TestCalculator:
    def setup_method(self):
        self.obj = Calculator()

    def test_multiply(self):
        self.result = self.obj.multiply(1, 2)
        assert self.result is not None  # Basic check

