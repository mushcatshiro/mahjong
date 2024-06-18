import pytest

from model import PlayAction


def test_eq():
    a1 = PlayAction(action="peng", target_tile="1万", discard_tile="2万")
    a2 = PlayAction(action="peng", target_tile="1万", discard_tile="2万")
    a3 = PlayAction(action="peng", target_tile="2万", discard_tile="3万")

    assert a1 == a2
    assert a1 != a3


def test_post_init():
    a1 = PlayAction(action="peng", target_tile="1万", discard_tile="2万")

    with pytest.raises(AssertionError):
        a1 = PlayAction(action="not_peng", target_tile="1万", discard_tile="2万")

    with pytest.raises(AssertionError):
        a1 = PlayAction(action="peng")

    with pytest.raises(AssertionError):
        a1 = PlayAction(action="peng", target_tile="1万")

    with pytest.raises(AssertionError):
        a1 = PlayAction(action="discard")
