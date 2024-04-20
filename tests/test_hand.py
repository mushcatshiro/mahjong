from game import Hand, TilesSequence, PlayAction


def reset_hand(h: Hand):
        h.tiles = []
        h.distinct_tile_count = {}
        h.tiles_history = {}
        h.non_playable_tiles = []
        h.locked_tiles = []


def test_hand(monkeypatch):
    # test for human readable format
    def mock_get_shang_candidates(self):
        pass

    monkeypatch.setattr(Hand, "get_shang_candidates", mock_get_shang_candidates)

    ts = TilesSequence()
    ts.shuffle(0)

    h = Hand(0)
    assert len(h.tiles) == 0

    for i in range(36):
        drawed = ts.draw(4)
        h.add_tiles(drawed)
        assert sorted(h.tiles_history[f"{i}add"]) == sorted(drawed)

    for idx, tile in enumerate(["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万"]):
        h.remove_tile(tile)
        assert h.distinct_tile_count[tile] == 3
        assert (
            h.tiles_history[f"{idx+36}remove"] == tile
        )  # `add_tiles` was called 36 times

def test_remove_tile():
    h = Hand(0)
    h.add_tiles(["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万"])
    h.remove_tile("1万")
    assert h.distinct_tile_count["1万"] == 0
    assert "1万" not in h.tiles
    reset_hand(h)

    h.add_tiles(["1万", "1万", "1万"])
    h.remove_tile("1万")
    assert h.distinct_tile_count["1万"] == 2
    assert h.tiles == ["1万", "1万"]
    h.remove_tile("1万")
    h.remove_tile("1万")
    assert h.distinct_tile_count["1万"] == 0
    assert h.tiles == []


def test_add_tiles():
    h = Hand(0)
    replacement_tile_count = h.add_tiles(["1万", "2万"])
    assert h.tiles == ["1万", "2万"]
    assert replacement_tile_count == 0

    replacement_tile_count = h.add_tiles(["菊"])
    assert h.tiles == ["1万", "2万"]
    assert h.non_playable_tiles == ["菊"]
    assert replacement_tile_count == 1


def test_get_shang_candidates():
    h = Hand(0)
    h.add_tiles(["1万", "2万"])
    assert h.get_shang_candidates() == ["3万"]

    h.add_tiles(["5万"])
    assert h.get_shang_candidates() == ["3万"]

    h.tiles = []  # reset
    h.add_tiles(["2万", "3万"])
    assert h.get_shang_candidates() == ["1万", "4万"]

    h.add_tiles(["4筒", "5筒"])
    assert h.get_shang_candidates() == ["1万", "4万", "3筒", "6筒"]

    h.add_tiles(["7索", "9索"])
    assert h.get_shang_candidates() == ["1万", "4万", "3筒", "6筒", "8索"]

def test_get_peng_candidates():
    h = Hand(0)
    h.add_tiles(["2万", "2万"])
    assert h.get_peng_candidates() == ["2万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "3万"])
    assert h.get_peng_candidates() == ["3万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万"])
    assert h.get_peng_candidates() == []

def test_get_gang_candidates():
    h = Hand(0)
    h.add_tiles(["2万", "2万", "2万"])
    assert h.get_gang_candidates() == ["2万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "3万", "3万"])
    assert h.get_gang_candidates() == ["3万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万", "4万"])
    assert h.get_gang_candidates() == []
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万", "5万"])
    assert h.get_gang_candidates() == []


def test_get_discardable_tiles():
    """
    TODO: `discard_tile` is not used, maybe use `Hand.resolve` instead?
    """
    h = Hand(0)
    h.add_tiles(["2万", "2万", "2万"])
    action = PlayAction(resolve=True, action="peng", input_tile= "2万", discard_tile="")
    h.peng(action)
    assert h.get_discardable_tiles() == []
    reset_hand(h)

    h.add_tiles(["2万", "2万", "2万", "2万"])
    action = PlayAction(resolve=True, action="an_gang", input_tile= "2万", discard_tile="")
    h.gang(action)
    assert h.get_discardable_tiles() == []
    reset_hand(h)

    h.add_tiles(["2万", "3万", "3万", "3万"])
    action = PlayAction(resolve=True, action="peng", input_tile= "3万", discard_tile="")
    h.peng(action)
    assert h.get_discardable_tiles() == ["2万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万"])
    assert h.get_discardable_tiles() == ["2万", "3万", "4万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万", "5万"])
    assert h.get_discardable_tiles() == ["2万", "3万", "4万", "5万"]


def test_is_winning_hand():
    h = Hand(0)
    # h.add_tiles(["1万", "2万", "3万", "1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "9万", "9万"])
    # assert h.is_winning_hand() == True

    # 对对胡
    h.add_tiles(["1万", "1万", "2万", "2万", "3万", "3万", "4万", "4万", "5万", "5万", "6万", "6万", "7万", "7万"])
    assert h.is_winning_hand() == True
    reset_hand(h)

    # 十三幺
    h.add_tiles(["1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "中", "發", "白", "白"])
    assert h.is_winning_hand() == True
    reset_hand(h)
