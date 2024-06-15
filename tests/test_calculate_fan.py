import calculate_fan
import fan

# fmt: off

def calculate(rf: calculate_fan.ResultFan):
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=[],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
    )


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
    assert rf.exclude == {"自摸"}
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
    assert rf.exclude == {"自摸"}
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

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=[],
        history={"1-hu-shang-add": "5万"},
        tiles=["4万", "5万", "5万", "5万", "6万"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
    )
    assert rf.fan_names == ["坎张"]
    assert rf.exclude == set()
    assert rf.total_fan == 1

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


def test_calculate_attribute_fan():
    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["4索", "4索", "4索", "6索", "6索", "發", "發", "發"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=["2索", "3索", "4索"],
        an_gang_history=["8索", "8索", "8索", "8索"],
        jiangs="",
    )
    assert rf.fan_names == ["绿一色"]
    assert rf.exclude == {"混一色"}
    assert rf.total_fan == 88

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1万", "1万", "1万", "2万", "3万", "4万", "5万", "5万", "6万", "7万", "8万", "9万", "9万", "9万"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["九莲宝灯"]
    assert rf.exclude == {"清一色", "不求人", "门前清", "无字", "幺九刻"}
    assert rf.total_fan == 88

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1筒", "1筒", "1筒", "9筒", "9筒", "9筒", "1索", "1索"],
        distinct_tiles={},
        peng_history=["1万", "1万", "1万", "9万", "9万", "9万"],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="",
    )
    assert rf.fan_names == ["清幺九"]
    assert rf.exclude == {"混幺九", "碰碰和", "全带幺", "双同刻", "幺九刻", "无字"}
    assert rf.total_fan == 64

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["西", "西", "西", "北", "北", "北", "中", "中", "發", "發", "發", "白", "白", "白"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="中",
    )
    assert rf.fan_names == ["字一色"]
    assert rf.exclude == {"混幺九", "碰碰和", "全带幺", "幺九刻"}
    assert rf.total_fan == 64

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1万", "9万", "1万", "9万", "1万", "9万", "1筒", "1筒", "1筒", "南", "南", "南", "白", "白"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="白",
    )
    assert rf.fan_names == ["混幺九", "缺一门"]
    assert rf.exclude == {"幺九刻", "碰碰和", "全带幺"}
    assert rf.total_fan == 33

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["2万", "2万", "2万", "4万", "4万", "4万", "6万", "6万", "6万", "8万", "8万", "8万", "2筒", "2筒"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="2筒",
    )
    assert rf.fan_names == ["全双刻", "缺一门"]
    assert rf.exclude == {"碰碰和", "断幺", "无字"}
    assert rf.total_fan == 25

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东", "东", "东", "南", "南"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="南",
    )
    assert rf.fan_names == ["混一色"]
    assert rf.exclude == set()
    assert rf.total_fan == 6

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "7万", "8万", "9万", "9万", "9万"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="9万",
    )
    assert rf.fan_names == ["清一色"]
    assert rf.exclude == {"无字"}
    assert rf.total_fan == 24

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["7万", "7万", "7万", "7索", "8索", "9索", "8筒", "8筒", "8筒", "7万", "8万", "9万", "9索", "9索"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="9索"
    )
    assert rf.fan_names == ["全大"]
    assert rf.exclude == {"大于五", "无字"}
    assert rf.total_fan == 24

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["4万", "5万", "6万", "4索", "4索", "4索", "5筒", "5筒", "5筒", "4万", "5万", "6万", "6索", "6索"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="6索",
    )
    assert rf.fan_names == ["全中"]
    assert rf.exclude == {"断幺", "无字"}
    assert rf.total_fan == 24

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1万", "2万", "3万", "1索", "2索", "3索", "1筒", "2筒", "3筒", "1万", "2万", "3万", "1索", "1索"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="1索",
    )
    assert rf.fan_names == ["全小"]
    assert rf.exclude == {"小于五", "无字"}
    assert rf.total_fan == 24

    rf = calculate_fan.ResultFan()
    tiles = ["3万", "4万", "5万", "5万", "5万", "3筒", "4筒", "5筒", "5筒", "6筒", "7筒", "5索", "5索", "5索"]
    distinct_tiles = calculate_fan.get_distinct_tiles(tiles)
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=tiles,
        distinct_tiles=distinct_tiles,
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["全带五"]
    assert rf.exclude == {"断幺", "无字"}
    assert rf.total_fan == 16

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["6万", "7万", "8万", "9万", "9万", "6万", "7万", "8万", "6筒", "7筒", "8筒", "6索", "7索", "8索"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="9万",
    )
    assert rf.fan_names == ["大于五"]
    assert rf.exclude == {"无字"}
    assert rf.total_fan == 12

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1万", "2万", "3万", "4万", "4万", "1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "2索", "3索"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="4万",
    )
    assert rf.fan_names == ["小于五"]
    assert rf.exclude == {"无字"}
    assert rf.total_fan == 12

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1筒", "2筒", "3筒", "1筒", "2筒", "3筒", "6索", "6索", "6索", "8索",  "8索",  "8索", "白", "白"],
        distinct_tiles={},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="白",
    )
    assert rf.fan_names == ["推不倒"]
    assert rf.exclude == {"缺一门"}
    assert rf.total_fan == 8

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1万", "1万", "1万", "2万", "2万", "2万", "3万", "3万", "3万", "4万", "4万", "4万", "5万", "5万"],
        distinct_tiles={"1万": 3, "2万": 3, "3万": 3, "4万": 3, "5万": 2},
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["清一色", "碰碰和"]
    assert rf.exclude == {"无字"}
    assert rf.total_fan == 30


    rf = calculate_fan.ResultFan()
    tiles = ["1万", "2万", "3万", "9万", "9万", "1筒", "1筒", "1筒", "7筒", "8筒", "9筒", "白", "白", "白"]
    distinct_tiles = calculate_fan.get_distinct_tiles(tiles)
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=tiles,
        distinct_tiles=distinct_tiles,
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="9万",
    )
    assert rf.fan_names == ["全带幺", "缺一门"]
    assert rf.exclude == set()
    assert rf.total_fan == 5

    rf = calculate_fan.ResultFan()
    tiles = ["3万", "4万", "5万", "6万", "6万", "3筒", "4筒", "5筒", "5筒", "6筒", "7筒", "5索", "5索", "5索"]
    distinct_tiles = calculate_fan.get_distinct_tiles(tiles)
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=tiles,
        distinct_tiles=distinct_tiles,
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="6万",
    )
    assert rf.fan_names == ["断幺"]
    assert rf.exclude == {"无字"}
    assert rf.total_fan == 2
