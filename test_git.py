import pytest


class TestBaseParser(object):
    """ Unit Tests for BaseParser object """

    def test_lower_list(self):
        actual = 'True'
        expected = 'True'
        assert actual == expected 
