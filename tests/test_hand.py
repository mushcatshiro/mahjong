from game import Hand, TilesSequence, PlayAction, PlayResult


def reset_hand(h: Hand):
    h.tiles = []
    h.distinct_tile_count = {}
    h.tiles_history = {}
    h.flower_tiles = []
    h.peng_history = []
    h.gang_history = []


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
    assert h.flower_tiles == ["菊"]
    assert replacement_tile_count == 1


def test_get_shang_candidates():
    h = Hand(0)
    h.add_tiles(["1万", "2万"])
    assert h.get_shang_candidates() == ["3万"]
    reset_hand(h)

    h.add_tiles(["1万", "2万", "5万"])
    assert h.get_shang_candidates() == ["3万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万"])
    assert h.get_shang_candidates() == ["1万", "4万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4筒", "5筒"])
    assert h.get_shang_candidates() == ["1万", "4万", "3筒", "6筒"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4筒", "5筒", "7索", "9索"])
    assert h.get_shang_candidates() == ["1万", "4万", "3筒", "6筒", "8索"]
    reset_hand(h)

    # dealing with repeated tiles
    h.add_tiles(["1万", "2万", "2万"])
    assert h.get_shang_candidates() == ["3万"]
    reset_hand(h)

    # dealing with locked tiles
    h.add_tiles(["1万", "2万", "2万", "2万"])
    h.peng_history.append("2万")
    assert h.get_shang_candidates() == []
    reset_hand(h)

    h.add_tiles(["1万", "2万", "2万", "2万", "2万"])
    h.gang_history.append("2万")
    assert h.get_shang_candidates() == []
    reset_hand(h)


def test_get_peng_candidates():
    h = Hand(0)
    h.add_tiles(["2万", "2万", "2万", "3万"])
    assert len(h.get_peng_candidates()) == 1
    assert h.get_peng_candidates()[0] == PlayAction(
        resolve=True, action="peng", target_tile="2万", discard_tile="3万"
    )
    reset_hand(h)

    h.add_tiles(["2万", "2万", "3万"])
    assert len(h.get_peng_candidates("2万")) == 1
    assert h.get_peng_candidates("2万")[0] == PlayAction(
        resolve=True, action="peng", target_tile="2万", add_tile=True, discard_tile="3万"
    )
    reset_hand(h)

    h.add_tiles(["2万", "3万", "3万", "3万"])
    assert len(h.get_peng_candidates()) == 1
    assert h.get_peng_candidates()[0] == PlayAction(
        resolve=True, action="peng", target_tile="3万", discard_tile="2万"
    )
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万"])
    assert h.get_peng_candidates() == []


def test_peng():
    h = Hand(0)

    # peng during a call
    h.add_tiles(["2万", "2万", "3万"])
    action = h.get_peng_candidates("2万")
    assert len(action) == 1
    play_result: PlayResult = h.peng(action[0])
    assert play_result.discarded_tile == "3万"
    assert h.tiles == ["2万", "2万", "2万"]
    assert h.peng_history == ["2万"]
    assert h.is_locked("2万")
    reset_hand(h)

    # check if there is 3 of a set
    h.add_tiles(["2万", "2万", "2万", "3万"])
    action = h.get_peng_candidates()
    assert len(action) == 1
    play_result: PlayResult = h.peng(action[0])
    assert play_result.discarded_tile == "3万"
    assert h.tiles == ["2万", "2万", "2万"]
    assert h.peng_history == ["2万"]
    assert h.is_locked("2万")


def test_get_gang_candidates():
    h = Hand(0)
    h.add_tiles(["2万", "2万", "2万"])
    assert len(h.get_gang_candidates(played_tile="2万")) == 1
    assert h.get_gang_candidates(played_tile="2万")[0] == PlayAction(
        resolve=True, action="ming_gang", add_tile=True, target_tile="2万"
    )
    reset_hand(h)

    h.add_tiles(["2万", "3万", "3万"])
    action = h.get_peng_candidates("3万")
    assert len(action) == 1
    h.peng(action[0])
    assert len(h.get_gang_candidates(drawed_tile="3万")) == 1
    assert h.get_gang_candidates(drawed_tile="3万")[0] == PlayAction(
        resolve=True, action="jia_gang", target_tile="3万"
    )
    reset_hand(h)

    h.add_tiles(["3万", "3万", "3万"])
    h.add_tiles(["3万"])
    assert len(h.get_gang_candidates(drawed_tile="3万")) == 1
    assert h.get_gang_candidates(drawed_tile="3万")[0] == PlayAction(
        resolve=True, action="an_gang", target_tile="3万"
    )
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万", "4万"])
    assert h.get_gang_candidates("5万") == []
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万", "5万"])
    assert h.get_gang_candidates("6万") == []


def test_gang():
    h = Hand(0)
    h.add_tiles(["2万", "2万", "2万"])
    action = h.get_gang_candidates(played_tile="2万")
    assert len(action) == 1
    assert action[0].action == "ming_gang"
    play_result: PlayResult = h.gang(action[0])
    assert play_result.need_replacement
    assert h.tiles == ["2万", "2万", "2万", "2万"]
    assert h.gang_history == ["2万"]
    assert h.is_locked("2万")
    reset_hand(h)

    # is confusing but drawed tiles should be added at `Player` level
    # before resolving stuff at `Hand`
    h.add_tiles(["2万", "2万", "2万"])
    h.add_tiles(["2万"])
    action = h.get_gang_candidates(drawed_tile="2万")
    assert len(action) == 1
    assert action[0].action == "an_gang"
    play_result: PlayResult = h.gang(action[0])
    assert play_result.need_replacement
    assert h.tiles == ["2万", "2万", "2万", "2万"]
    assert h.gang_history == ["2万"]
    assert h.is_locked("2万")
    reset_hand(h)

    h.add_tiles(["2万", "2万", "1万"])
    action = h.get_peng_candidates(played_tile="2万")
    assert len(action) == 1
    assert action[0].action == "peng"
    play_result: PlayResult = h.peng(action[0])
    assert h.tiles == ["2万", "2万", "2万"]
    assert h.peng_history == ["2万"]
    h.add_tiles(["2万"])
    action = h.get_gang_candidates(drawed_tile="2万")
    assert len(action) == 1
    assert action[0].action == "jia_gang"
    play_result = h.gang(action[0])
    assert play_result.need_replacement
    assert h.tiles == ["2万", "2万", "2万", "2万"]
    assert h.gang_history == ["2万"]
    assert h.is_locked("2万")
    reset_hand(h)


def test_get_discardable_tiles():
    """
    TODO: `discard_tile` is not used, maybe use `Hand.resolve` instead?
    """
    h = Hand(0)
    h.add_tiles(["2万", "2万", "2万", "3万"])
    action = h.get_peng_candidates()
    assert len(action) == 1
    h.peng(action[0])
    assert h.get_discardable_tiles() == []
    reset_hand(h)

    h.add_tiles(["2万", "2万", "2万", "2万"])
    action = PlayAction(
        resolve=True, action="an_gang", target_tile="2万", discard_tile=""
    )
    h.gang(action)
    assert h.get_discardable_tiles() == []
    reset_hand(h)

    h.add_tiles(["2万", "3万", "3万", "3万", "4万"])
    action = h.get_peng_candidates()
    assert len(action) == 2
    h.peng(action[0])
    assert h.get_discardable_tiles() == [action[1].discard_tile]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万"])
    assert h.get_discardable_tiles() == ["2万", "3万", "4万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万", "5万"])
    assert h.get_discardable_tiles() == ["2万", "3万", "4万", "5万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万", "5万", "6万"])
    assert h.get_discardable_tiles(exclude_tile="6万") == ["2万", "3万", "4万", "5万"]
    reset_hand(h)

    h.add_tiles(["2万", "3万", "4万", "5万", "6万"])
    assert h.get_discardable_tiles(exclude_tile=["5万", "6万"]) == ["2万", "3万", "4万"]


def test_is_winning_hand():
    # TODO
    h = Hand(0)
    # h.add_tiles(["1万", "2万", "3万", "1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "9万", "9万"])
    # assert h.is_winning_hand() == True

    # 对对胡
    h.add_tiles(
        [
            "1万",
            "1万",
            "2万",
            "2万",
            "3万",
            "3万",
            "4万",
            "4万",
            "5万",
            "5万",
            "6万",
            "6万",
            "7万",
            "7万",
        ]
    )
    assert h.is_winning_hand() == True
    reset_hand(h)

    # 十三幺
    h.add_tiles(
        ["1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "中", "發", "白", "白"]
    )
    assert h.is_winning_hand() == True
    reset_hand(h)

    # standard winning hand 3/3/3/3 + 2


def test_get_eye_candidates():
    h = Hand(0)
    h.add_tiles(["2万", "2万"])
    eye_candidates = h.get_eye_candidates()
    assert len(eye_candidates) == 1
    assert eye_candidates == ["2万"]
    reset_hand(h)

    h.add_tiles(["2万", "2万", "3万", "3万"])
    eye_candidates = h.get_eye_candidates()
    assert len(eye_candidates) == 2
    assert sorted(eye_candidates) == sorted(["2万", "3万"])
    reset_hand(h)

    h.add_tiles(["2万", "2万", "2万"])
    eye_candidates = h.get_eye_candidates()
    assert len(eye_candidates) == 1
    assert eye_candidates == ["2万"]
    reset_hand(h)

    # is a hack
    h.add_tiles(["2万", "2万", "2万"])
    h.peng_history.append("2万")
    eye_candidates = h.get_eye_candidates()
    assert len(eye_candidates) == 0
    reset_hand(h)

    # is a hack
    h.add_tiles(["2万", "2万", "2万", "2万"])
    h.peng_history.append("2万")
    eye_candidates = h.get_eye_candidates()
    assert len(eye_candidates) == 0
    reset_hand(h)


def test_get_valid_shang_sets():
    h = Hand(0)

    # 1/2/3
    h.add_tiles(["1万", "2万", "3万"])
    valid_sequences = h.get_valid_shang_sets()
    assert len(valid_sequences) == 1
    assert valid_sequences[0] == ["1万", "2万", "3万"]
    reset_hand(h)

    # 1/2/3/4
    h.add_tiles(["1万", "2万", "3万", "4万"])
    valid_sequences = h.get_valid_shang_sets()
    assert len(valid_sequences) == 2
    assert ["1万", "2万", "3万"] in valid_sequences
    assert ["2万", "3万", "4万"] in valid_sequences
    reset_hand(h)

    # peng
    h.add_tiles(["1万", "1万", "1万", "2万", "3万"])
    h.peng_history.append("1万")  # is a hack
    valid_sequences = h.get_valid_shang_sets()
    assert len(valid_sequences) == 0
    reset_hand(h)


def test_internal_dp_search():
    h = Hand(0)
    # BUG dp search should look for `eyes` before moving to `peng` and `gang`
    resp = h._dp_search(["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万"])
    assert 0 in resp
    assert resp[0] == []


def test_resolve():
    h = Hand(0)

    # resolve peng
    h.add_tiles(["2万", "2万", "2万", "3万"])
    actions = h.get_peng_candidates()
    assert len(actions) == 1
    play_result = h.resolve(actions[0])
    assert h.tiles == ["2万", "2万", "2万"]
    assert h.peng_history == ["2万"]
    assert h.is_locked("2万")
    assert play_result.discarded_tile == "3万"
    reset_hand(h)

    # resolve an_gang
    h.add_tiles(["2万", "2万", "2万", "2万"])
    actions = h.get_gang_candidates(drawed_tile="2万")
    assert len(actions) == 1
    play_result = h.resolve(actions[0])
    assert h.tiles == ["2万", "2万", "2万", "2万"]
    assert h.gang_history == ["2万"]
    assert h.is_locked("2万")
    assert play_result.need_replacement
    reset_hand(h)

    # resolve jia_gang
    h.add_tiles(["2万", "2万", "2万", "3万"])
    actions = h.get_peng_candidates()
    assert len(actions) == 1
    play_result = h.resolve(actions[0])
    assert play_result.discarded_tile == "3万"
    h.add_tiles(["2万"])
    actions = h.get_gang_candidates(drawed_tile="2万")
    assert len(actions) == 1
    play_result = h.resolve(actions[0])
    assert h.tiles == ["2万", "2万", "2万", "2万"]
    assert h.gang_history == ["2万"]
    assert h.is_locked("2万")
    assert play_result.need_replacement
    reset_hand(h)

    # resolve ming_gang
    h.add_tiles(["2万", "2万", "2万"])
    actions = h.get_gang_candidates(played_tile="2万")
    assert len(actions) == 1
    play_result = h.resolve(actions[0])
    assert h.tiles == ["2万", "2万", "2万", "2万"]
    assert h.gang_history == ["2万"]
    assert h.is_locked("2万")
    assert play_result.need_replacement
    reset_hand(h)
