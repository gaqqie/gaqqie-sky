import pytest

from gaqqie_sky.common import util


def test_generate_id():
    actual = util.generate_id()
    assert type(actual) == str
    assert len(actual) == 36


def test_get_datetime_str():
    actual = util.get_datetime_str()
    assert type(actual) == str
    assert len(actual) == 24


def test_get_cors_response_headers():
    actual = util.get_cors_response_headers()
    assert type(actual) == dict
    keys = actual.keys()
    assert "Access-Control-Allow-Headers" in keys
    assert "Access-Control-Allow-Origin" in keys
    assert "Access-Control-Allow-Methods" in keys
