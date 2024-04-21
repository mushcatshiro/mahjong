import pytest

from game import PlayAction, PengAction


def test_eq():
    a1 = PlayAction(resolve=True, action="peng", input_tile="1万", discard_tile="2万")
    a2 = PlayAction(resolve=True, action="peng", input_tile="1万", discard_tile="2万")
    a3 = PlayAction(resolve=True, action="peng", input_tile="2万", discard_tile="3万")

    assert a1 == a2
    assert a1!= a3


def test_post_init():
    a1 = PlayAction(resolve=True, action="peng", input_tile="1万", discard_tile="2万")

    with pytest.raises(AssertionError):
        a1 = PlayAction(resolve=True, action="not_peng", input_tile="1万", discard_tile="2万")
    
    with pytest.raises(AssertionError):
        a1 = PlayAction(resolve=False, action="peng", input_tile="1万", discard_tile="2万")

    with pytest.raises(AssertionError):
        a1 = PlayAction(resolve=True, action="peng")

    with pytest.raises(AssertionError):
        a1 = PlayAction(resolve=True, action="peng", input_tile="1万")

    with pytest.raises(AssertionError):
        a1 = PlayAction(resolve=False, action="discard")
