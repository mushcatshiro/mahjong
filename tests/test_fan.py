import calculate_fan
import fan


# fmt: off


def test_get_suites():
    tiles = ["1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "2索", "3索", "东", "南", "西", "北", "中", "发", "白", "春", "夏", "梅", "蘭"]
    suites = calculate_fan.get_suites(tiles)
    assert suites == {
        "万": ["1", "2", "3"],
        "筒": ["1", "2", "3"],
        "索": ["1", "2", "3"],
    }


def test_kan_zhang():
    assert fan.kan_zhang(
        {"万": ["4", "5", "5", "5", "6"]},
        {"1-hu-shang-add": "5万"},
    )
    assert not fan.kan_zhang(
        {"万": ["4", "5", "5", "5", "6"]},
        {"1-turn-draw-add": "5万"},
    )
    assert not fan.kan_zhang(
        {"万": ["4", "5", "5", "5", "6"]},
        {"1-hu-jiang-add": "西"},
    )
    assert not fan.kan_zhang(
        {"万": ["1", "2", "2", "2", "3"]},
        {"1-hu-shang-add": "1万"},
    )
    assert not fan.kan_zhang(
        {"万": ["7", "8", "8", "8", "9"]},
        {"1-hu-shang-add": "9万"},
    )
    assert not fan.kan_zhang(
        {"万": ["4", "5", "5", "6", "7"]},
        {"1-hu-shang-add": "5万"},
    )


def test_bian_du():
    assert fan.bian_du(
        {"万": ["1", "2", "3"]},
        {"1-hu-shang-add": "3万"},
    )
    assert fan.bian_du(
        {"万": ["1", "1", "2", "2", "3", "3"]},
        {"1-hu-shang-add": "3万"},
    )
    assert fan.bian_du(
        {"万": ["7", "8", "9"]},
        {"1-hu-shang-add": "7万"},
    )
    assert fan.bian_du(
        {"万": ["7", "7", "8", "8", "9", "9"]},
        {"1-hu-shang-add": "7万"},
    )
    assert not fan.bian_du(
        {"万": ["1", "2", "3", "3", "4", "5"]},
        {"1-hu-shang-add": "5万"},
    )
    assert not fan.bian_du(
        {"万": ["5", "6", "7", "7", "8", "9"]},
        {"1-hu-shang-add": "3万"},
    )
    assert not fan.bian_du(
        {"万": ["5", "6", "7", "7", "8", "9"]},
        {"1-hu-shang-add": "7万"},
    )


def test_wu_zi():
    assert fan.wu_zi(["1万", "9万", "1筒", "9筒"])
    assert not fan.wu_zi(["1筒", "2筒", "3筒", "西"])
    assert not fan.wu_zi(["1筒", "2筒", "3筒", "白"])


def test_que_yi_men():
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万"]
    )
    assert not fan.que_yi_men(merged_suites)
    merged_suites = calculate_fan.get_suites(["1万", "2万", "3万", "1筒"])
    assert fan.que_yi_men(merged_suites)
    merged_suites = calculate_fan.get_suites(["1万", "2万", "3万", "1筒", "2筒", "3筒", "白"])
    assert fan.que_yi_men(merged_suites)
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "2索", "3索"]
    )
    assert not fan.que_yi_men(merged_suites)


def test_yao_jiu_ke():
    assert fan.yao_jiu_ke({"1万": 3}) == 1
    assert fan.yao_jiu_ke({"1万": 3, "东": 1}) == 1
    assert fan.yao_jiu_ke({"1万": 3, "9万": 1}) == 1
    assert fan.yao_jiu_ke({"1万": 3, "9万": 3, "东": 3}) == 3
    assert fan.yao_jiu_ke({"1万": 3, "9万": 3, "东": 3, "白": 3}) == 3
    assert fan.yao_jiu_ke({"3万": 3, "2万": 3}) == 0


def test_lao_shao_fu():
    hand_suites = {
        "万": ["1", "2", "3", "7", "8", "9"],
        "筒": ["1", "2", "3"],
        "索": ["1", "2", "3"],
    }
    assert fan.lao_shao_fu(hand_suites) == 1
    hand_suites = {
        "筒": ["1", "2", "3"],
        "索": ["1", "2", "3"],
    }
    assert fan.lao_shao_fu(hand_suites) == 0
    hand_suites = {
        "万": ["1", "2", "3", "7", "8", "9"],
        "筒": ["1", "2", "3", "7", "8", "9"],
    }
    assert fan.lao_shao_fu(hand_suites) == 2
    hand_suites = {
        "万": ["1", "2", "4", "7", "8", "万"],
    }
    assert fan.lao_shao_fu(hand_suites) == 0


def test_lian_liu():
    suites = {}
    assert fan.lian_liu(suites) == 0
    assert fan.lian_liu({"万": ["1万", "2万", "3万", "4万", "5万", "6万"]}) == 1
    assert (
        fan.lian_liu({"万": ["1万", "2万", "3万", "4万", "5万", "6万", "7万"]}) == 1
    )


def test_duan_yao():
    assert fan.duan_yao(["2万", "3万", "4万", "5万"])
    assert not fan.duan_yao(["1万", "2万", "3万", "4万"])
    assert not fan.duan_yao(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万"]
    )
    assert not fan.duan_yao(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东"]
    )
    assert not fan.duan_yao(["2万", "3万", "4万", "5万", "6万", "7万", "8万", "白"])


def test_shi_san_yao():
    assert fan.shi_san_yao(
        ["1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "中", "發", "白", "白"]
    )
    assert fan.shi_san_yao(
        ["1万", "1万", "9万", "1筒", "9筒", "1索", "9索", "东", "南", "西", "北", "中", "發", "白"]
    )


def test_si_gui_yi():
    assert fan.si_gui_yi(
        {"1万": 2, "2万": 4, "3万": 4, "4万": 2, "中": 2},
        [],
        [],
    ) == 2
    assert not fan.si_gui_yi(
        {"1万": 2, "2万": 4, "3万": 4, "4万": 2, "中": 2},
        ["1万", "1万", "1万", "1万"],
        [],
    )
    assert not fan.si_gui_yi(
        {"1万": 2, "2万": 4, "3万": 4, "4万": 2, "中": 2},
        [],
        ["1万", "1万", "1万", "1万"],
    )



def test_ping_hu():
    pass


def test_men_qian_qing():
    assert fan.men_qian_qing(
        {"1-turn-draw-add": "1万"},
    )
    assert not fan.men_qian_qing(
        {"1-shang-add-add": "1万"},
    )
    assert not fan.men_qian_qing(
        {"1-peng-add-add": "1万"},
    )
    assert not fan.men_qian_qing(
        {"1-ming_gang-move": "1万"},
    )
    assert not fan.men_qian_qing(
        {"1-jia_gang-move": "1万"},
    )
    assert fan.men_qian_qing(
        {"1-an-gang-move": "1万"},
    )


def test_bu_qiu_ren():
    assert fan.bu_qiu_ren(
        {"1-turn-draw-add": "1万"},
        [],
        [],
        []
    )
    assert not fan.bu_qiu_ren(
        {"1-hu-add-add": "1万"},
        [],
        [],
        []
    )
    assert not fan.bu_qiu_ren(
        {"1-turn-draw-add": "1万"},
        ["1万", "1万", "1万", "1万"],
        [],
        []
    )


def test_quan_dai_yao():
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["1万", "9万", "1万", "9万", "1万", "9万", "1筒", "1筒", "1筒", "南", "南", "南", "白", "白"]
    )
    assert fan.quan_dai_yao(distinct_tiles, [], [], [], [], "白")
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["1万", "9万", "1万", "9万", "1万", "9万", "南", "南", "南", "白", "白"]
    )
    assert fan.quan_dai_yao(
        distinct_tiles,
        ["1筒", "1筒", "1筒"],
        [],
        [],
        [],
        "白"
    )
    distinct_tiles = calculate_fan.get_distinct_tiles(
        ["2万", "3万", "4万", "5万", "6万", "7万", "1筒", "1筒", "1筒", "南", "南", "南", "白", "白"]
    )
    assert not fan.quan_dai_yao(distinct_tiles, [], [], [], [], "白"
    )


def test_quan_qiu_ren():
    assert fan.quan_qiu_ren(
        ["5万", "5万"],
        [],
        {"1-hu-add-add": "5万"},
    )
    # one an ke
    assert not fan.quan_qiu_ren(
        ["1万", "1万", "1万", "5万", "5万"],
        [],
        {"1-hu-add-add": "5万"},
    )
    # zi mo
    assert not fan.quan_qiu_ren(
        ["5万", "5万"],
        [],
        {"1-turn-draw-add": "5万"},
    )

def test_wu_men_qi():
    assert fan.wu_men_qi(
        {
            "万": ["1", "2", "3"],
            "筒": ["4", "5", "6"],
            "索": ["7", "8", "9"],
        },
        {
            "1万": 1, "2万": 1, "3万": 1,
            "4筒": 1, "5筒": 1, "6筒": 1,
            "7索": 1, "8索": 1, "9索": 1,
            "东": 3, "白": 2,
        }
    )
    assert not fan.wu_men_qi(
        {"万": ["1", "2", "3", "4", "5", "6", "7", "8", "9"]},
        {
            "1万": 1, "2万": 1, "3万": 1, "4万": 1, "5万": 1, "6万": 1, "7万": 1,
            "8万": 1, "9万": 1, "东": 3, "南": 2}
    )


def test_hun_yi_se():
    assert fan.hun_yi_se(
        {"万": ["1", "2", "3", "4", "5", "6", "7", "8", "9"]},
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东", "东", "东", "南", "南"]
    )
    assert not fan.hun_yi_se(
        {"万": ["1", "1", "1", "2", "3", "4", "5", "6", "7", "7", "8", "8", "9", "9"]},
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "7万", "8万", "9万", "1万", "1万"]
    )


def test_peng_peng_hu():
    assert fan.peng_peng_hu(
        {"1万": 3, "2万": 3, "3万": 3, "4万": 3, "5万": 2},
    )


def test_san_se_san_jie_gao():
    merged_suites = calculate_fan.get_suites(
        ["1万", "1万", "1万", "2筒", "2筒", "2筒", "3索", "3索", "3索", "东", "东", "东", "南", "南"]
    )
    assert fan.san_se_san_jie_gao(merged_suites)
    merged_suites = calculate_fan.get_suites(
        ["1万", "1万", "1万", "2筒", "2筒", "2筒", "3索", "3索", "3索", "4索", "4索", "4索", "南", "南"]
    )
    assert fan.san_se_san_jie_gao(merged_suites)
    merged_suites = calculate_fan.get_suites(
        ["1万", "1万", "1万", "3筒", "3筒", "3筒", "3索", "3索", "3索", "4索", "4索", "4索", "南", "南"]
    )
    assert not fan.san_se_san_jie_gao(merged_suites)


def test_tui_bu_dao():
    assert fan.tui_bu_dao(
        ["1筒", "2筒", "3筒", "1筒", "2筒", "3筒", "6索", "6索", "6索", "8索",  "8索",  "8索", "白", "白"]
    )
    assert not fan.tui_bu_dao(
        ["1筒", "2筒", "3筒", "1筒", "2筒", "3筒", "6索", "6索", "6索", "8索",  "8索",  "8索", "發", "發"]
    )
    assert not fan.tui_bu_dao(
        ["1万", "2万", "3筒", "1筒", "2筒", "3筒", "6索", "6索", "6索", "8索",  "8索",  "8索", "白", "白"]
    )


def test_xiao_yu_wu():
    assert fan.xiao_yu_wu(
        ["1万", "2万", "3万", "4万", "4万", "1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "2索", "3索"]
    )
    assert not fan.xiao_yu_wu(
        ["1万", "2万", "3万", "發", "發", "1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "2索", "3索"]
    )
    assert not fan.xiao_yu_wu(
        ["1万", "2万", "3万", "9万", "9万", "1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "2索", "3索"]
    )


def test_da_yu_wu():
    assert fan.da_yu_wu(
        ["6万", "7万", "8万", "9万", "9万", "6万", "7万", "8万", "6筒", "7筒", "8筒", "6索", "7索", "8索"]
    )
    assert not fan.da_yu_wu(
        ["6万", "7万", "8万", "發", "發", "6万", "7万", "8万", "6筒", "7筒", "8筒", "6索", "7索", "8索"]
    )
    assert not fan.da_yu_wu(
        ["6万", "7万", "8万", "1万", "1万", "6万", "7万", "8万", "6筒", "7筒", "8筒", "6索", "7索", "8索"]
    )


def test_zu_he_long():
    exists, _ = fan.zu_he_long(
        {"万": ["1", "4", "7"], "筒": ["2", "5", "8"], "索": ["3", "6", "9"]}
    )
    assert exists
    exists, ref = fan.zu_he_long(
        {"万": ["1", "4", "7", "7", "8", "9"], "筒": ["2", "5", "8"], "索": ["3", "6", "9"]}
    )
    assert exists
    assert ref == {"万": ["1", "4", "7"], "筒": ["2", "5", "8"], "索": ["3", "6", "9"]}


def test_quan_bu_kao():
    assert fan.quan_bu_kao(
        {
            "南": 1, "西": 1, "北": 1, "中": 1, "發": 1, "白": 1,
            "1万": 1, "4万": 1, "7万": 1,
            "2筒": 1, "5筒": 1, "8筒": 1,
            "3索": 1, "6索": 1
        },
        {"万": ["1", "4", "7"], "筒": ["2", "5", "8"], "索": ["3", "6"]}
    )


def quan_dai_wu():
    assert fan.quan_dai_wu(
        ["3万", "4万", "5万", "5万", "5万", "3筒", "4筒", "5筒", "5筒", "6筒", "7筒", "5索", "5索", "5索"]
    )
    assert not fan.quan_dai_wu(
        ["1万", "2万", "3万", "5万", "5万", "3筒", "4筒", "5筒", "5筒", "6筒", "7筒", "5索", "5索", "5索"]
    )
    assert not fan.quan_dai_wu(
        ["3万", "4万", "5万", "白", "白", "3筒", "4筒", "5筒", "5筒", "6筒", "7筒", "5索", "5索", "5索"]
    )
    assert not fan.quan_dai_wu(
        ["3万", "4万", "5万", "西", "西", "3筒", "4筒", "5筒", "5筒", "6筒", "7筒", "5索", "5索", "5索"]
    )


def test_san_se_shuang_long_hui():
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "7万", "8万", "9万", "1筒", "2筒", "3筒", "7筒", "8筒", "9筒", "5索", "5索"]
    )
    assert fan.san_se_shuang_long_hui(
        merged_suites
    )
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "7万", "8万", "9万", "1筒", "2筒", "3筒", "7筒", "8筒", "9筒", "6索", "6索"]
    )
    assert not fan.san_se_shuang_long_hui(
        merged_suites
    )


def test_quan_xiao():
    assert fan.quan_xiao(
        ["1万", "2万", "3万", "1索", "2索", "3索", "1筒", "2筒", "3筒", "1万", "2万", "3万", "1索", "1索"]
    )
    assert not fan.quan_xiao(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "1筒", "1筒", "1筒", "1索", "1索"]
    )
    assert not fan.quan_xiao(
        ["1万", "2万", "3万", "1索", "2索", "3索", "1筒", "2筒", "3筒", "1万", "2万", "3万", "白", "白"]
    )


def test_quan_zhong():
    assert fan.quan_zhong(
        ["4万", "5万", "6万", "4索", "4索", "4索", "5筒", "5筒", "5筒", "4万", "5万", "6万", "6索", "6索"]
    )
    assert not fan.quan_zhong(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "1筒", "1筒", "1筒", "1索", "1索"]
    )
    assert not fan.quan_zhong(
        ["4万", "5万", "6万", "4索", "4索", "4索", "5筒", "5筒", "5筒", "4万", "5万", "6万", "白", "白"]
    )


def test_quan_da():
    assert fan.quan_da(
        ["7万", "7万", "7万", "7索", "8索", "9索", "8筒", "8筒", "8筒", "7万", "8万", "9万", "9索", "9索"]
    )
    assert not fan.quan_da(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "1筒", "1筒", "1筒", "1索", "1索"]
    )
    assert not fan.quan_da(
        ["7万", "7万", "7万", "7索", "8索", "9索", "8筒", "8筒", "8筒", "7万", "8万", "9万", "白", "白"]
    )


def test_yi_se_san_jie_gao():
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "1万", "2万", "3万", "1万", "2万", "3万", "1筒", "2筒", "3筒", "1索", "1索"]
    )
    assert fan.yi_se_san_jie_gao(
        merged_suites
    )
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "1筒", "2筒", "3筒", "1索", "1索"]
    )
    assert not fan.yi_se_san_jie_gao(
        merged_suites
    )


def test_qing_yi_se():
    assert fan.qing_yi_se(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "7万", "8万", "9万", "9万", "9万"],
        {
            "万": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
        }
    )
    assert not fan.qing_yi_se(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "7万", "8万", "9万", "9筒", "9筒"],
        {
            "万": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
            "筒": ["9"],
        }
    )
    assert not fan.qing_yi_se(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "7万", "8万", "9万", "白", "白"],
        {
            "万": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
        }
    )


def test_quan_shuang_ke():
    assert fan.quan_shuang_ke(
        ["2万", "2万", "2万", "4万", "4万", "4万", "6万", "6万", "6万", "8万", "8万", "8万", "2筒", "2筒"]
    )
    assert not fan.quan_shuang_ke(
        ["2万", "2万", "2万", "4万", "4万", "4万", "6万", "6万", "6万", "8万", "8万", "8万", "1筒", "1筒"]
    )
    assert not fan.quan_shuang_ke(
        ["2万", "2万", "2万", "4万", "4万", "4万", "6万", "6万", "6万", "8万", "8万", "8万", "白", "白"]
    )


def test_qi_xing_bu_kao():
    assert fan.qi_xing_bu_kao(
        {
            "东": 1, "南": 1, "西": 1, "北": 1, "中": 1, "發": 1, "白": 1,
            "1万": 1, "4万": 1, "7万": 1,
            "2筒": 1, "5筒": 1,
            "3索": 1, "6索": 1
        },
        {"万": ["1", "4", "7"], "筒": ["2", "5"], "索": ["3", "6"]}
    )
    assert not fan.qi_xing_bu_kao(
        {
            "南": 1, "西": 1, "北": 1, "中": 1, "發": 1, "白": 1,
            "1万": 1, "4万": 1, "7万": 1,
            "2筒": 1, "5筒": 1, "8筒": 1,
            "3索": 1, "6索": 1
        },
        {"万": ["1", "4", "7"], "筒": ["2", "5", "8"], "索": ["3", "6"]}
    )
    assert not fan.qi_xing_bu_kao(
        {
            "东": 1, "南": 1, "西": 1, "北": 1, "中": 1, "發": 1, "白": 1,
            "1万": 1, "4万": 1, "7万": 1,
            "2筒": 1, "5筒": 1, "9筒": 1,
            "3索": 1, "6索": 1
        },
        {"万": ["1", "4", "7"], "筒": ["2", "5", "9"], "索": ["3", "6"]}
    )

def test_qi_dui():
    assert fan.qi_dui(
        {"1万": 2, "2万": 2, "3万": 2, "4万": 2, "5万": 2, "6万": 2, "7万": 2}
    )
    assert not fan.qi_dui(
        {"1万": 3, "2万": 3, "3万": 3, "4万": 3, "5万": 2}
    )


def test_hun_yao_jiu():
    assert fan.hun_yao_jiu(
        ["1万", "9万", "1万", "9万", "1万", "9万", "1筒", "1筒", "1筒", "南", "南", "南", "白", "白"]
    )
    assert not fan.hun_yao_jiu(
        ["2万", "9万", "2万", "9万", "2万", "9万", "1筒", "1筒", "1筒", "南", "南", "南", "白", "白"]
    )


def test_yi_se_si_jie_gao():
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "4万", "1万", "2万", "3万", "4万", "1万", "2万", "3万", "4万", "白", "白"]
    )
    assert fan.yi_se_si_jie_gao(merged_suites)
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "4万", "1万", "2万", "3万", "4万", "1万", "2万", "3万", "4万", "5万", "5万"]
    )
    assert fan.yi_se_si_jie_gao(merged_suites)
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "1万", "2万", "3万", "1万", "2万", "3万", "1万", "2万", "3万", "白", "白"]
    )
    assert not fan.yi_se_si_jie_gao(merged_suites)
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "4万", "2万", "3万", "4万", "5万", "3万", "5万", "5万", "6万", "白", "白"]
    )
    assert not fan.yi_se_si_jie_gao(merged_suites)


def test_yi_se_si_tong_shun():
    assert fan.yi_se_si_tong_shun(
        ["1万", "2万", "3万", "1万", "2万", "3万", "1万", "2万", "3万", "1万", "2万", "3万"],
    )
    assert not fan.yi_se_si_tong_shun(
        ["1万", "2万", "3万", "1万", "2万", "3万", "1万", "2万", "3万", "2万", "3万", "4万"],
    )
    assert not fan.yi_se_si_tong_shun(
        ["1万", "2万", "3万", "4万", "1万", "2万", "3万", "4万", "1万", "2万", "3万", "4万"]
    )


def test_yi_se_shuang_long_hui():
    # assumes that lao shao fu is calculated correctly
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "7万", "8万", "9万", "1万", "2万", "3万", "7万", "8万", "9万", "5万", "5万"]
    )
    assert fan.yi_se_shuang_long_hui(
        merged_suites
    )
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "7万", "8万", "9万", "1万", "2万", "3万", "7万", "8万", "9万", "6万", "6万"]
    )
    assert not fan.yi_se_shuang_long_hui(
        merged_suites
    )


def test_zi_yi_se():
    assert fan.zi_yi_se(
        ["西", "西", "西", "北", "北", "北", "中", "中", "發", "發", "發", "白", "白", "白"]
    )
    assert not fan.zi_yi_se(
        ["西", "西", "西", "北", "北", "北", "1索", "1索", "發", "發", "發", "白", "白", "白"]
    )


def test_qing_yao_jiu():
    assert fan.qing_yao_jiu(
        ["1万", "1万", "1万", "9万", "9万", "9万", "1筒", "1筒", "1筒", "9筒", "9筒", "9筒", "1索", "1索"]
    )
    assert not fan.qing_yao_jiu(
        ["1万", "1万", "1万", "9万", "9万", "9万", "1筒", "1筒", "1筒", "9筒", "9筒", "9筒", "2索", "2索"]
    )
    assert not fan.qing_yao_jiu(
        ["1万", "1万", "1万", "9万", "9万", "9万", "1筒", "1筒", "1筒", "9筒", "9筒", "9筒", "白", "白"]
    )


def test_lian_qi_dui():
    assert fan.lian_qi_dui(
        ["1万", "1万", "2万", "2万", "3万", "3万", "4万", "4万", "5万", "5万", "6万", "6万", "7万", "7万"]
    )
    assert fan.lian_qi_dui(
        ["1万", "1万", "2万", "2万", "3万", "3万", "4万", "4万", "5万", "5万", "6万", "6万", "7万", "7万"]
    )
    assert not fan.lian_qi_dui(
        ["1万", "1万", "2万", "3万", "4万", "3万", "4万", "5万", "5万", "6万", "7万", "6万", "7万", "8万"]
    )
    assert not fan.lian_qi_dui(
        ["1万", "1万", "白", "白", "3万", "3万", "4万", "4万", "5万", "5万", "6万", "6万", "7万", "7万", "8万"]
    )


def test_jiu_lian_bao_deng():
    merged_suites = calculate_fan.get_suites(
        ["1万", "1万", "1万", "2万", "3万", "4万", "5万", "5万", "6万", "7万", "8万", "9万", "9万", "9万"]
    )
    assert fan.jiu_lian_bao_deng(
        merged_suites,
        ["1万", "1万", "1万", "2万", "3万", "4万", "5万", "5万", "6万", "7万", "8万", "9万", "9万", "9万"]
    )
    merged_suites = calculate_fan.get_suites(
        ["1筒", "1筒", "1筒", "2筒", "2筒", "3筒", "4筒", "5筒", "6筒", "7筒", "8筒", "9筒", "9筒", "9筒"]
    )
    merged_suites = calculate_fan.get_suites(
        ["1筒", "1筒", "1筒", "2筒", "2筒", "3筒", "4筒", "5筒", "6筒", "7筒", "8筒", "9筒", "9筒", "9筒"]
    )
    assert fan.jiu_lian_bao_deng(
        merged_suites,
        ["1筒", "1筒", "1筒", "2筒", "2筒", "3筒", "4筒", "5筒", "6筒", "7筒", "8筒", "9筒", "9筒", "9筒"]
    )
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东"]
    )
    assert not fan.jiu_lian_bao_deng(
        merged_suites,
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东"]
    )
    merged_suites = calculate_fan.get_suites(
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东", "發"]
    )
    assert not fan.jiu_lian_bao_deng(
        merged_suites,
        ["1万", "2万", "3万", "4万", "5万", "6万", "7万", "8万", "9万", "东", "發"]
    )
    merged_suites = calculate_fan.get_suites(
        ["1万", "1万", "1万", "2万", "3万", "4万", "5万", "5万", "6筒", "7筒", "8筒", "9筒", "9筒", "9筒"]
    )
    assert not fan.jiu_lian_bao_deng(
        merged_suites,
        ["1万", "1万", "1万", "2万", "3万", "4万", "5万", "5万", "6筒", "7筒", "8筒", "9筒", "9筒", "9筒"]
    )


def test_lv_yi_se():
    assert not fan.lv_yi_se(
        ["1索", "2索", "3索", "4索", "5索", "6索", "7索", "8索", "9索", "东"]
    )
    assert fan.lv_yi_se(["2索", "3索", "4索", "6索", "8索", "發"])
