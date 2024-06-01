import calculate_fan


def test_calculate_win_mode_fan():
    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=["妙手回春", "自摸"],
        history={},
        tiles=[],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
    )
    assert rf.fan_names == ["妙手回春", "不求人"]
    assert rf.exclude == {"自摸", "门前清"}
    assert rf.total_fan == 12

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=["海底捞月"],
        history={"1-peng-add-add": "1万"},
        tiles=[],
        distinct_tiles={},
        peng_history=["1万", "1万", "1万"],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
    )
    assert rf.fan_names == ["海底捞月"]
    assert rf.exclude == {
        "自摸",
    }
    assert rf.total_fan == 8

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=["杠上开花"],
        history={"1-gang-add-add": "1万"},
        tiles=[],
        distinct_tiles={},
        peng_history=[],
        gang_history=["1万", "1万", "1万", "1万"],
        shang_history=[],
        an_gang_history=[],
    )
    assert rf.fan_names == ["杠上开花"]
    assert rf.exclude == {
        "自摸",
    }
    assert rf.total_fan == 8

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=["抢杠和", "自摸"],
        history={"1-hu-add-add": "1万"},
        tiles=[],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=["1万", "2万", "3万"],
        an_gang_history=[],
    )
    assert rf.fan_names == ["抢杠和", "门前清"]
    assert rf.exclude == {"自摸", "和绝张"}
    assert rf.total_fan == 10

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=[],
        history={"1-shang-add-add": "1万", "2-hu-add-add": "發"},
        tiles=["發", "發"],
        distinct_tiles={"發": 2},
        peng_history=[],
        gang_history=[],
        shang_history=["1万", "2万", "3万"],
        an_gang_history=[],
    )
    assert rf.fan_names == ["全求人"]
    assert rf.exclude == {"单骑对子", "自摸"}
    assert rf.total_fan == 6

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=["自摸"],
        history={"1-shang-add-add": "1万", "2-turn-draw-add": "1万"},
        tiles=[],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=["1万", "2万", "3万"],
        an_gang_history=[],
    )
    assert rf.fan_names == ["自摸"]
    assert rf.exclude == set()
    assert rf.total_fan == 1

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=["和绝张"],
        history={},
        tiles=[],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
    )
    assert rf.fan_names == ["和绝张"]
    assert rf.exclude == set()
    assert rf.total_fan == 4

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=[],
        history={"1-hu-shang-add": "3万"},
        tiles=["1万", "2万", "3万"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
    )
    assert rf.fan_names == ["边张"]
    assert rf.exclude == set()
    assert rf.total_fan == 1

    # FIXME
    # rf = calculate_fan.ResultFan()
    # calculate_fan.calculate_win_mode_fan(
    #     rf,
    #     winning_condition=[],
    #     history={"1-hu-peng-add": "5万"},
    #     tiles=["4万", "5万", "5万", "5万", "6万"],
    #     distinct_tiles={},
    #     peng_history=[],
    #     gang_history=[],
    #     shang_history=[],
    #     an_gang_history=[],
    # )
    # assert rf.fan_names == ["坎张"]
    # assert rf.exclude == set()
    # assert rf.total_fan == 1

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=["单骑对子"],
        history={},
        tiles=[],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
    )
    assert rf.fan_names == ["单骑对子"]
    assert rf.exclude == set()
    assert rf.total_fan == 1
