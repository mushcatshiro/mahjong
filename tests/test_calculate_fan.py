import calculate_fan
import pytest

# fmt: off

def test_calculate_win_mode_fan():
    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=["妙手回春", "自摸"],
        history={"0": {"action": "add", "play_action": "draw", "tile": "5万"}},
        tiles=[],
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
        history={"0": {"action": "add", "play_action": "peng", "tile": "1万"}},
        tiles=[],
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
        history={"0": {"action": "add", "play_action": "gang", "tile": "1万"}},
        tiles=[],
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
        winning_condition=["抢杠和"],
        history={"0": {"action": "hu-add", "play_action": "shang", "tile": "1万"}},
        tiles=[],
        peng_history=[],
        gang_history=[],
        shang_history=["1万", "2万", "3万"],
        an_gang_history=[],
    )
    assert rf.fan_names == ["抢杠和"]
    assert rf.exclude == {"和绝张"}
    assert rf.total_fan == 8

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=[],
        history={
            "0": {"action": "add", "play_action": "shang", "tile": "1万"},
            "1": {"action": "hu-add", "play_action": "jiang", "tile": "發"}
        },
        tiles=["發", "發"],
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
        history={
            "0": {"action": "add", "play_action": "shang", "tile": "1万"},
            "1": {"action": "add", "play_action": "draw", "tile": "1万"}
        },
        tiles=[],
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
        history={"0": {"action": "hu-add", "play_action": "shang", "tile": "1万"}},
        tiles=[],
        peng_history=[],
        gang_history=[],
        shang_history=["1万", "2万", "3万"],
        an_gang_history=[],
    )
    assert rf.fan_names == ["和绝张"]
    assert rf.exclude == set()
    assert rf.total_fan == 4

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=[],
        history={"0": {"action": "hu-add", "play_action": "shang", "tile": "3万"}},
        tiles=["1万", "2万", "3万"],
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
        history={"0": {"action": "hu-add", "play_action": "shang", "tile": "5万"}},
        tiles=["5万", "5万"],
        peng_history=[],
        gang_history=[],
        shang_history=["4万", "5万", "6万"],
        an_gang_history=[],
    )
    assert rf.fan_names == ["全求人", "坎张"]
    assert rf.exclude == {"单骑对子", "自摸"}
    assert rf.total_fan == 7

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_win_mode_fan(
        rf,
        winning_condition=["单骑对子"],
        history={"0": {"action": "hu-add", "play_action": "jiang", "tile": "5万"}},
        tiles=["5万", "5万", "1万", "1万", "1万"],
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
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="9万",
    )
    assert rf.fan_names == ["清一色", "平和", "四归一"]
    assert rf.exclude == {"无字"}
    assert rf.total_fan == 28

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["7万", "7万", "7万", "7索", "8索", "9索", "8筒", "8筒", "8筒", "7万", "8万", "9万", "9索", "9索"],
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="9索"
    )
    assert rf.fan_names == ["全大", "四归一"]
    assert rf.exclude == {"大于五", "无字"}
    assert rf.total_fan == 26

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["4万", "5万", "6万", "4索", "4索", "4索", "5筒", "5筒", "5筒", "4万", "5万", "6万", "6索", "6索"],
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
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="1索",
    )
    assert rf.fan_names == ["全小", "全带幺"]
    assert rf.exclude == {"小于五", "无字"}
    assert rf.total_fan == 28

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["3万", "4万", "5万", "5万", "5万", "3筒", "4筒", "5筒", "5筒", "6筒", "7筒", "5索", "5索", "5索"],
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
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="9万",
    )
    assert rf.fan_names == ["大于五", "平和"]
    assert rf.exclude == {"无字"}
    assert rf.total_fan == 14

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1万", "2万", "3万", "4万", "4万", "1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "2索", "3索"],
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="4万",
    )
    assert rf.fan_names == ["小于五", "平和"]
    assert rf.exclude == {"无字"}
    assert rf.total_fan == 14

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1筒", "2筒", "3筒", "1筒", "2筒", "3筒", "6索", "6索", "6索", "8索",  "8索",  "8索", "白", "白"],
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
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["1万", "2万", "3万", "9万", "9万", "1筒", "1筒", "1筒", "7筒", "8筒", "9筒", "白", "白", "白"],
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
    calculate_fan.calculate_attribute_fan(
        rf,
        tiles=["3万", "4万", "5万", "6万", "6万", "3筒", "4筒", "5筒", "5筒", "6筒", "7筒", "5索", "5索", "5索"],
        peng_history=[],
        gang_history=[],
        shang_history=[],
        an_gang_history=[],
        jiangs="6万",
    )
    assert rf.fan_names == ["断幺"]
    assert rf.exclude == {"无字"}
    assert rf.total_fan == 2


def test_calculate_ke_gang_fan():
    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万"],
        gang_history=[],
        an_gang_history=["1万", "1万", "1万", "1万", "2万", "2万", "2万", "2万", "3万", "3万", "3万", "3万", "4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["四杠", "四暗刻"]
    assert rf.total_fan == 152
    assert rf.exclude == {"碰碰和", "单骑对子", "不求人", "门前清"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万"],
        gang_history=["1万", "1万", "1万", "1万"],
        an_gang_history=["2万", "2万", "2万", "2万", "3万", "3万", "3万", "3万", "4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["四杠", "三暗刻"]
    assert rf.total_fan == 104
    assert rf.exclude == {"碰碰和", "单骑对子"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万"],
        gang_history=["1万", "1万", "1万", "1万", "2万", "2万", "2万", "2万"],
        an_gang_history=["3万", "3万", "3万", "3万", "4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["四杠", "双暗刻"]
    assert rf.total_fan == 90
    assert rf.exclude == {"碰碰和", "单骑对子"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万"],
        gang_history=["1万", "1万", "1万", "1万", "2万", "2万", "2万", "2万", "3万", "3万", "3万", "3万"],
        an_gang_history=["4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["四杠"]
    assert rf.total_fan == 88
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "1万", "1万"],
        gang_history=[],
        an_gang_history=["2万", "2万", "2万", "2万", "3万", "3万", "3万", "3万", "4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["三杠", "四暗刻"]
    assert rf.total_fan == 96
    assert rf.exclude == {"碰碰和", "不求人", "门前清"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "2万", "3万"],
        gang_history=[],
        an_gang_history=["2万", "2万", "2万", "2万", "3万", "3万", "3万", "3万", "4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["三杠", "三暗刻"]
    assert rf.total_fan == 48
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "1万", "1万"],
        gang_history=["2万", "2万", "2万", "2万"],
        an_gang_history=["3万", "3万", "3万", "3万", "4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["三杠", "三暗刻"]
    assert rf.total_fan == 48
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "2万", "3万"],
        gang_history=["2万", "2万", "2万", "2万"],
        an_gang_history=["3万", "3万", "3万", "3万", "4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["三杠", "双暗刻"]
    assert rf.total_fan == 34
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "1万", "1万"],
        gang_history=["2万", "2万", "2万", "2万", "4万", "4万", "4万", "4万"],
        an_gang_history=["3万", "3万", "3万", "3万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["三杠", "双暗刻"]
    assert rf.total_fan == 34
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "2万", "3万"],
        gang_history=["2万", "2万", "2万", "2万", "4万", "4万", "4万", "4万"],
        an_gang_history=["3万", "3万", "3万", "3万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["三杠"]
    assert rf.total_fan == 32
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "1万", "1万", "2万", "2万", "2万"],
        gang_history=[],
        an_gang_history=["4万", "4万", "4万", "4万", "3万", "3万", "3万", "3万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["双暗杠", "四暗刻"]
    assert rf.total_fan == 70
    assert rf.exclude == {"碰碰和", "不求人", "门前清"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "7万", "8万", "9万", "2万", "2万", "2万"],
        gang_history=[],
        an_gang_history=["4万", "4万", "4万", "4万", "3万", "3万", "3万", "3万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["双暗杠", "三暗刻"]
    assert rf.total_fan == 22
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "1万", "1万", "2万", "2万", "2万"],
        gang_history=["4万", "4万", "4万", "4万"],
        an_gang_history=["3万", "3万", "3万", "3万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["明暗杠", "三暗刻"]
    assert rf.total_fan == 21
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "7万", "8万", "9万", "2万", "2万", "2万"],
        gang_history=["4万", "4万", "4万", "4万"],
        an_gang_history=["3万", "3万", "3万", "3万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["明暗杠", "双暗刻"]
    assert rf.total_fan == 7
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "1万", "1万", "2万", "2万", "2万"],
        gang_history=["4万", "4万", "4万", "4万", "3万", "3万", "3万", "3万"],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["双明杠", "双暗刻"]
    assert rf.total_fan == 6
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "1万", "1万", "2万", "2万", "2万", "3万", "3万", "3万"],
        gang_history=[],
        an_gang_history=["4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["暗杠", "四暗刻"]
    assert rf.total_fan == 66
    assert rf.exclude == {"碰碰和", "不求人", "门前清"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "2万", "3万", "2万", "2万", "2万", "3万", "3万", "3万"],
        gang_history=[],
        an_gang_history=["4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["暗杠", "三暗刻"]
    assert rf.total_fan == 18
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "2万", "3万", "7万", "8万", "9万", "3万", "3万", "3万"],
        gang_history=[],
        an_gang_history=["4万", "4万", "4万", "4万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["暗杠", "双暗刻"]
    assert rf.total_fan == 4
    assert rf.exclude == set() # 101

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "1万", "1万", "2万", "2万", "2万", "3万", "3万", "3万"],
        gang_history=["4万", "4万", "4万", "4万"],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["明杠", "三暗刻"]
    assert rf.total_fan == 17
    assert rf.exclude == set() # 13

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "5万", "6万", "7万", "2万", "2万", "2万", "3万", "3万", "3万"],
        gang_history=["4万", "4万", "4万", "4万"],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["明杠", "双暗刻"]
    assert rf.total_fan == 3
    assert rf.exclude == set() # 12

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "5万", "6万", "7万", "5万", "6万", "7万"],
        gang_history=["4万", "4万", "4万", "4万"],
        an_gang_history=["3万", "3万", "3万", "3万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["明暗杠"]
    assert rf.total_fan == 5
    assert rf.exclude == set() # 110

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万"],
        gang_history=["1万", "1万", "1万", "1万", "2万", "2万", "2万", "2万", "3万", "3万", "3万", "3万", "4万", "4万", "4万", "4万"],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["四杠"]
    assert rf.total_fan == 88
    assert rf.exclude == {"碰碰和", "单骑对子"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "1万", "1万", "1万", "2万", "2万", "2万", "3万", "3万", "3万", "4万", "4万", "4万"],
        gang_history=[],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["四暗刻"]
    assert rf.total_fan == 64
    assert rf.exclude == {"碰碰和", "不求人", "门前清"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "5万", "6万", "7万"],
        gang_history=["1万", "1万", "1万", "1万", "2万", "2万", "2万", "2万", "3万", "3万", "3万", "3万"],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["三杠"]
    assert rf.total_fan == 32
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "5万", "6万", "7万", "1万", "1万", "1万", "2万", "2万", "2万", "3万", "3万", "3万"],
        gang_history=[],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["三暗刻"]
    assert rf.total_fan == 16
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "5万", "6万", "7万", "7万", "8万", "9万"],
        gang_history=[],
        an_gang_history=["2万", "2万", "2万", "2万", "3万", "3万", "3万", "3万"],
        jiangs="5万",
    )
    assert rf.fan_names == ["双暗杠"]
    assert rf.total_fan == 6
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "5万", "6万", "7万", "7万", "8万", "9万"],
        gang_history=["2万", "2万", "2万", "2万", "3万", "3万", "3万", "3万"],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["双明杠"]
    assert rf.total_fan == 4
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "5万", "6万", "7万", "7万", "8万", "9万", "2万", "2万", "2万", "3万", "3万", "3万"],
        gang_history=[],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["双暗刻"]
    assert rf.total_fan == 2
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_ke_gang_fan(
        rf,
        tiles=["5万", "5万", "5万", "6万", "7万", "7万", "8万", "9万", "7万", "8万", "9万"],
        gang_history=["3万", "3万", "3万", "3万"],
        an_gang_history=[],
        jiangs="5万",
    )
    assert rf.fan_names == ["明杠"]  # correct fan 清一色 一般高 明杠
    assert rf.total_fan == 1
    assert rf.exclude == set()


def test_calculate_feng_ke_fan():
    rf = calculate_fan.ResultFan()
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["东", "东", "东", "南", "南", "南", "西", "西", "西", "北", "北", "北", "白", "白"]
    )
    calculate_fan.calculate_feng_ke_fan( rf, distinct_tiles=distinct_tiles)
    assert rf.fan_names == ["大四喜"]
    assert rf.total_fan == 88
    assert rf.exclude == {"圈风刻", "门风刻", "三风刻", "碰碰和", "幺九刻"}

    rf = calculate_fan.ResultFan()
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["1万", "1万", "1万", "南", "南", "南", "西", "西", "西", "北", "北", "北", "东", "东"]
    )
    calculate_fan.calculate_feng_ke_fan( rf, distinct_tiles=distinct_tiles)
    assert rf.fan_names == ["小四喜"]
    assert rf.total_fan == 64
    assert rf.exclude == {"三风刻", "幺九刻"}

    rf = calculate_fan.ResultFan()
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["1万", "1万", "1万", "南", "南", "南", "西", "西", "西", "北", "北", "北", "白", "白"]
    )
    calculate_fan.calculate_feng_ke_fan( rf, distinct_tiles=distinct_tiles)
    assert rf.fan_names == ["三风刻"]
    assert rf.total_fan == 12
    assert rf.exclude == set()


def test_calculate_jian_ke_fan():
    rf = calculate_fan.ResultFan()
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["中", "中", "中", "發", "發", "發", "白", "白", "白", "东", "东", "东", "南", "南"]
    )
    calculate_fan.calculate_jian_ke_fan(rf, distinct_tiles=distinct_tiles)
    assert rf.fan_names == ["大三元"]
    assert rf.total_fan == 88
    assert rf.exclude == {"双箭刻", "箭刻"}

    rf = calculate_fan.ResultFan()
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["中", "中", "中", "發", "發", "發", "南", "南", "南", "东", "东", "东", "白", "白"]
    )
    calculate_fan.calculate_jian_ke_fan(rf, distinct_tiles=distinct_tiles)
    assert rf.fan_names == ["小三元"]
    assert rf.total_fan == 64
    assert rf.exclude == {"双箭刻", "箭刻"}

    rf = calculate_fan.ResultFan()
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["中", "中", "中", "發", "發", "發", "南", "南", "南", "东", "东", "东", "西", "西"]
    )
    calculate_fan.calculate_jian_ke_fan(rf, distinct_tiles=distinct_tiles)
    assert rf.fan_names == ["双箭刻"]
    assert rf.total_fan == 6
    assert rf.exclude == {"箭刻"}


def test_calculate_tong_ke_fan():
    rf = calculate_fan.ResultFan()
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["1万", "1万", "1万", "1索", "1索", "1索", "1筒", "1筒", "1筒", "4万", "4万", "4万", "5万", "5万"]
    )
    calculate_fan.calculate_tong_ke_fan(rf, distinct_tiles=distinct_tiles)
    assert rf.fan_names == ["三同刻"]
    assert rf.total_fan == 16

    rf = calculate_fan.ResultFan()
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["1万", "1万", "1万", "1索", "1索", "1索", "3万", "3万", "3万", "4万", "4万", "4万", "5万", "5万"]
    )
    calculate_fan.calculate_tong_ke_fan(rf, distinct_tiles=distinct_tiles)
    assert rf.fan_names == ["双同刻"]
    assert rf.total_fan == 2


def test_calculate_shang_fan():
    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "1万"],
        shang_history=[],
        jiangs="1万",
    )
    assert rf.fan_names == []
    assert rf.total_fan == 0
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "1万", "2万", "3万", "1万", "2万", "3万", "1万", "2万", "3万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["一色四同顺"]
    assert rf.total_fan == 48
    assert rf.exclude == {"一色三节高", "一般高", "四归一", "七对", "四归一", "一般高"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "2万", "3万", "4万", "3万", "4万", "5万", "4万", "5万", "6万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["一色四步高"]
    assert rf.total_fan == 32
    assert rf.exclude == {"连六", "老少副"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "1万", "2万", "3万", "1万", "2万", "3万", "9万", "9万", "9万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["一色三同顺"]
    assert rf.total_fan == 24
    assert rf.exclude == {"一色三节高", "一般高"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "3万", "4万", "5万", "5万", "6万", "7万", "9万", "9万", "9万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["一色三步高"]
    assert rf.total_fan == 16
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "1万", "2万", "3万", "4万", "5万", "6万", "4万", "5万", "6万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["一般高x2"]
    assert rf.total_fan == 2
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "1万", "2万", "3万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["一般高", "清龙"]
    assert rf.total_fan == 17
    assert rf.exclude == {"连六", "老少副"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "1索", "2索", "3索", "1筒", "2筒", "3筒", "1万", "2万", "3万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["一般高", "三色三同顺"]
    assert rf.total_fan == 9
    assert rf.exclude == {"喜相逢"}

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "2索", "3索", "4索", "3筒", "4筒", "5筒", "1万", "2万", "3万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["一般高", "三色三步高"]
    assert rf.total_fan == 7
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "4索", "5索", "6索", "7筒", "8筒", "9筒", "1万", "2万", "3万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["一般高", "花龙"]
    assert rf.total_fan == 9
    assert rf.exclude == set()

    rf = calculate_fan.ResultFan()
    calculate_fan.calculate_shang_fan(
        rf,
        tiles=["1万", "2万", "3万", "1索", "2索", "3索", "5筒", "6筒", "7筒", "5万", "6万", "7万", "5索", "5索"],
        shang_history=[],
        jiangs="5索",
    )
    assert rf.fan_names == ["喜相逢x2"]
    assert rf.total_fan == 2
    assert rf.exclude == set()


def test_calculate_fan_simple():
    pass


@pytest.mark.skipif("not config.getoption('exhaustive')")
def test_calculate_fan_exhaustive():
    pass
