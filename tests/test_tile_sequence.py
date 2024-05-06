from game import TilesSequence

import pytest


def test_basics():
    # test for human readable format
    ts = TilesSequence()
    assert len(ts.tiles) == 144

    for i in range(2, 13):
        ts.shuffle(i)
        assert len(ts.tiles) == 144
        assert ts.tiles != ts.initial_sequence

    cumsum = 0

    cur_head = [ts.tiles[0]]
    drawed = ts.draw(1)
    cumsum += 1
    assert drawed[0] == cur_head[0]
    assert len(ts.tiles) == 144 - cumsum

    cur_head = ts.tiles[:4]
    drawed = ts.draw(4)
    cumsum += 4
    for i in range(4):
        assert drawed[i] == cur_head[i]
    assert len(ts.tiles) == 144 - cumsum

    cur_head = [ts.tiles[0], ts.tiles[4]]
    drawed = ts.draw(2, jump=True)
    cumsum += 2
    for i in range(2):
        assert drawed[i] == cur_head[i]
    assert len(ts.tiles) == 144 - cumsum

    cur_tail = [ts.tiles[-1]]
    drawed = ts.replace(1)
    cumsum += 1
    assert drawed[0] == cur_tail[0]
    assert len(ts.tiles) == 144 - cumsum

    cur_tail = ts.tiles[-4:]
    drawed = ts.replace(4)
    cumsum += 4
    for i in range(4):
        assert drawed[i] in cur_tail
    assert len(ts.tiles) == 144 - cumsum

    with pytest.raises(AssertionError):
        ts.draw(1, jump=True)


def test_only_flowers():
    ts = TilesSequence()
    ts.tiles = ["春", "夏", "秋", "冬", "梅", "蘭", "竹", "菊"]
    assert ts.only_flowers()

    ts = TilesSequence()
    ts.tiles = ["春", "夏", "秋", "冬", "梅", "蘭", "竹", "1万"]
    assert not ts.only_flowers()
