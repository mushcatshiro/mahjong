import calculate_fan


def test_get_suites():
    # fmt: off
    tiles = ["1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "2索", "3索", "东", "南", "西", "北", "中", "发", "白", "春", "夏", "梅", "蘭"]
    # fmt: on
    suites = calculate_fan.get_suites(tiles)
    assert suites == {
        "万": ["1", "2", "3"],
        "筒": ["1", "2", "3"],
        "索": ["1", "2", "3"],
    }


def test_wu_zi():
    assert calculate_fan.wu_zi(["1万", "9万", "1筒", "9筒"])
    assert not calculate_fan.wu_zi(["1筒", "2筒", "3筒", "西"])
    assert not calculate_fan.wu_zi(["1筒", "2筒", "3筒", "白"])


def _test_ming_gang():
    assert calculate_fan.ming_gang(["1万", "1万", "1万", "1万"])
    assert not calculate_fan.ming_gang(["1万", "1万", "1万", "2万"])
    assert not calculate_fan.ming_gang(["1万", "1万", "1万", "1筒"])


def test_que_yi_men():
    assert not calculate_fan.que_yi_men(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万"]
    )
    assert calculate_fan.que_yi_men(["1万", "2万", "3万", "1筒"])
    assert calculate_fan.que_yi_men(["1万", "2万", "3万", "1筒", "2筒", "3筒", "白"])
    assert not calculate_fan.que_yi_men(
        ["1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "2索", "3索"]
    )


def test_yao_jiu_ke():
    assert calculate_fan.yao_jiu_ke({"1万": 3}) == 1
    assert calculate_fan.yao_jiu_ke({"1万": 3, "东": 1}) == 1
    assert calculate_fan.yao_jiu_ke({"1万": 3, "9万": 1}) == 1
    assert calculate_fan.yao_jiu_ke({"1万": 3, "9万": 3, "东": 3}) == 3
    assert calculate_fan.yao_jiu_ke({"1万": 3, "9万": 3, "东": 3, "白": 3}) == 3
    assert calculate_fan.yao_jiu_ke({"3万": 3, "2万": 3}) == 0


def test_lao_shao_fu():
    hand_suites = {
        "万": ["1", "2", "3", "7", "8", "9"],
        "筒": ["1", "2", "3"],
        "索": ["1", "2", "3"],
    }
    assert calculate_fan.lao_shao_fu(hand_suites) == 1
    hand_suites = {
        "筒": ["1", "2", "3"],
        "索": ["1", "2", "3"],
    }
    assert calculate_fan.lao_shao_fu(hand_suites) == 0
    hand_suites = {
        "万": ["1", "2", "3", "7", "8", "9"],
        "筒": ["1", "2", "3", "7", "8", "9"],
    }
    assert calculate_fan.lao_shao_fu(hand_suites) == 2
    hand_suites = {
        "万": ["1", "2", "4", "7", "8", "万"],
    }
    assert calculate_fan.lao_shao_fu(hand_suites) == 0


def test_lian_liu():
    suites = {}
    assert calculate_fan.lian_liu(suites) == 0
    assert calculate_fan.lian_liu({"万": ["1万", "2万", "3万", "4万", "5万", "6万"]}) == 1
    assert (
        calculate_fan.lian_liu({"万": ["1万", "2万", "3万", "4万", "5万", "6万", "7万"]}) == 1
    )


def test_duan_yao():
    assert calculate_fan.duan_yao(["2万", "3万", "4万", "5万"])
    assert not calculate_fan.duan_yao(["1万", "2万", "3万", "4万"])
    assert not calculate_fan.duan_yao(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万"]
    )
    assert not calculate_fan.duan_yao(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东"]
    )
    assert not calculate_fan.duan_yao(["2万", "3万", "4万", "5万", "6万", "7万", "8万", "白"])


def test_shi_san_yao():
    assert calculate_fan.shi_san_yao(
        ["1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "中", "發", "白", "白"]
    )
    assert calculate_fan.shi_san_yao(
        ["1万", "1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "中", "發", "白"]
    )


def test_yi_se_shuang_long_hui():
    # assumes that lao shao fu is calculated correctly
    # fmt: off
    assert calculate_fan.yi_se_shuang_long_hui(
        ["1万", "2万", "3万", "7万", "8万", "9万", "1万", "2万", "3万", "7万", "8万", "9万", "5万", "5万"],
        {"1万": 2, "2万": 2, "3万": 2, "7万": 2, "8万": 2, "9万": 2, "5万": 2},
    )
    assert not calculate_fan.yi_se_shuang_long_hui(
        ["1万", "2万", "3万", "7万", "8万", "9万", "1万", "2万", "3万", "7万", "8万", "9万", "6万", "6万"],
        {"1万": 2, "2万": 2, "3万": 2, "7万": 2, "8万": 2, "9万": 2, "6万": 2},
    )
    # fmt: on


def test_si_an_ke():
    assert calculate_fan.si_an_ke({"1万": 4, "2万": 4, "3万": 4, "4万": 4}, [])
    assert not calculate_fan.si_an_ke(
        {"1万": 4, "2万": 4, "3万": 4, "4万": 4}, ["4万", "4万", "4万", "4万"]
    )


def test_zi_yi_se():
    assert calculate_fan.zi_yi_se(
        ["西", "西", "西", "北", "北", "北", "中", "中", "發", "發", "發", "白", "白", "白"]
    )
    assert not calculate_fan.zi_yi_se(
        ["西", "西", "西", "北", "北", "北", "1索", "1索", "發", "發", "發", "白", "白", "白"]
    )


def test_qing_yao_jiu():
    # fmt: off
    assert calculate_fan.qing_yao_jiu(
        ["1万", "1万", "1万", "9万", "9万", "9万", "1筒", "1筒", "1筒", "9筒", "9筒", "9筒", "1索", "1索"]
    )
    assert not calculate_fan.qing_yao_jiu(
        ["1万", "1万", "1万", "9万", "9万", "9万", "1筒", "1筒", "1筒", "9筒", "9筒", "9筒", "2索", "2索"]
    )
    assert not calculate_fan.qing_yao_jiu(
        ["1万", "1万", "1万", "9万", "9万", "9万", "1筒", "1筒", "1筒", "9筒", "9筒", "9筒", "白", "白"]
    )
    # fmt: on


def test_lian_qi_dui():
    # fmt: off
    assert calculate_fan.lian_qi_dui(
        ["1万", "1万", "2万", "2万", "3万", "3万", "4万", "4万", "5万", "5万", "6万", "6万", "7万", "7万"]
    )
    assert calculate_fan.lian_qi_dui(
        ["1万", "1万", "2万", "2万", "3万", "3万", "4万", "4万", "5万", "5万", "6万", "6万", "7万", "7万"]
    )
    assert not calculate_fan.lian_qi_dui(
        ["1万", "1万", "2万", "3万", "4万", "3万", "4万", "5万", "5万", "6万", "7万", "6万", "7万", "8万"]
    )
    assert not calculate_fan.lian_qi_dui(
        ["1万", "1万", "白", "白", "3万", "3万", "4万", "4万", "5万", "5万", "6万", "6万", "7万", "7万", "8万"]
    )
    # fmt: on


def test_si_gang():
    assert calculate_fan.si_gang({"1万": 4, "2万": 4, "3万": 4, "4万": 4, "5万": 2}, "5万")
    assert not calculate_fan.si_gang(
        {"1万": 4, "2万": 3, "3万": 3, "4万": 2, "5万": 3}, "4万"
    )


def test_jiu_lian_bao_deng():
    # fmt: off
    assert calculate_fan.jiu_lian_bao_deng(["1万", "1万", "1万", "2万", "3万", "4万", "5万", "5万", "6万", "7万", "8万", "9万", "9万", "9万"])
    assert calculate_fan.jiu_lian_bao_deng(["1筒", "1筒", "1筒", "2筒", "2筒", "3筒", "4筒", "5筒", "6筒", "7筒", "8筒", "9筒", "9筒", "9筒"])
    assert not calculate_fan.jiu_lian_bao_deng(["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东"])
    assert not calculate_fan.jiu_lian_bao_deng(["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东", "發"])
    assert not calculate_fan.jiu_lian_bao_deng(["1万", "1万", "1万", "2万", "3万", "4万", "5万", "5万", "6筒", "7筒", "8筒", "9筒", "9筒", "9筒"])
    # fmt: on


def test_lv_yi_se():
    assert not calculate_fan.lv_yi_se(
        ["1索", "2索", "3索", "4索", "5索", "6索", "7索", "8索", "9索", "东"]
    )
    assert calculate_fan.lv_yi_se(["2索", "3索", "4索", "6索", "8索", "發"])
