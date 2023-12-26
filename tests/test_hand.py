from game import Hand, TilesSequence, Tiles, DEFAULT_REPLACEMENT_TILES


def test_hand(monkeypatch):
    # test for human readable format
    def mock_update_shang_candidates(self):
        pass

    monkeypatch.setattr(Hand, "update_shang_candidates", mock_update_shang_candidates)

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


def test_update_shang_candidates():
    h = Hand(0)
    h.add_tiles(["1万", "2万"])
    assert h.shang_candidates == ["3万"]

    h.add_tiles(["5万"])
    assert h.shang_candidates == ["3万"]

    h.tiles = []  # reset
    h.add_tiles(["2万", "3万"])
    assert h.shang_candidates == ["1万", "4万"]

    h.add_tiles(["4筒", "5筒"])
    assert h.shang_candidates == ["1万", "4万", "3筒", "6筒"]

    h.add_tiles(["7索", "9索"])
    assert h.shang_candidates == ["1万", "4万", "3筒", "6筒", "8索"]
