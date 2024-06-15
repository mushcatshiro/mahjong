from tiles import (
    FENGS,
    JIANS,
    HUAS,
    SHANGS,
    SHANG_REF,
    REVERSED_SHANG_LUT,
    SUITES,
)

import fan


class ResultFan:
    def __init__(self):
        self.total_fan = 0
        self.fan_names = []
        self.exclude = set()

    def __repr__(self):
        return f"{self.total_fan} {self.fan_names} {self.exclude}"


# -------- helper functions --------


def get_suites(tiles, shang_history=[]):
    suites = {}
    for tile in tiles + shang_history:
        if len(tile) == 2:
            if tile[1] not in suites:
                suites[tile[1]] = [tile[0]]
            else:
                suites[tile[1]].append(tile[0])
    return suites


def remove_zu_he_long(tiles: list, ref: dict):
    # remove tiles that are part of zu_he_long
    for suite, ref_tiles in ref.items():
        for ref_tile in ref_tiles:
            tiles.remove(ref_tile + suite)
    return tiles


def get_distinct_tiles(tiles: list):
    distinct_tiles = {}
    for tile in tiles:
        if tile not in distinct_tiles:
            distinct_tiles[tile] = 1
        else:
            distinct_tiles[tile] += 1
    return distinct_tiles


def check_shang(tile, tiles, jiangs):
    if len(tile) == 1:
        return False
    val = tile[0]
    suite = tile[1]
    merged_suites = get_suites(tiles)

    for ref in REVERSED_SHANG_LUT[val]:
        if ref[0] in merged_suites[suite] and ref[1] in merged_suites[suite]:
            return True
    return False


# -------- main functions --------


def calculate_win_mode_fan(
    rf: ResultFan,
    winning_condition: list,
    history,
    tiles,
    peng_history,
    gang_history,
    shang_history,
    an_gang_history,
):
    # 妙手回春: 摸最后一张牌成和牌、不计自摸
    if "妙手回春" in winning_condition:
        rf.fan_names.append("妙手回春")
        rf.total_fan += 8
        rf.exclude.add("自摸")
    # 海底捞月: 和本局打出的最后一张牌、不计自摸
    if "海底捞月" in winning_condition:
        rf.fan_names.append("海底捞月")
        rf.total_fan += 8
        rf.exclude.add("自摸")
    # 杠上开花: 和开杠后摸进的牌、不计自摸；不计杠来的花补花
    if "杠上开花" in winning_condition:
        rf.fan_names.append("杠上开花")
        rf.total_fan += 8
        rf.exclude.add("自摸")
    # 抢杠和: 和他家明刻加杠的牌，不计和绝张
    if "抢杠和" in winning_condition:
        rf.fan_names.append("抢杠和")
        rf.total_fan += 8
        rf.exclude.add("和绝张")
    # 全球人
    if fan.quan_qiu_ren(tiles, an_gang_history, history):
        rf.fan_names.append("全求人")
        rf.total_fan += 6
        rf.exclude.add("单骑对子")
        rf.exclude.add("自摸")
    # 不求人: 不计门前清、自摸
    if "不求人" not in rf.exclude and (
        "自摸" in winning_condition
        and fan.bu_qiu_ren(history, gang_history, peng_history, shang_history)
    ):
        rf.fan_names.append("不求人")
        rf.total_fan += 4
        rf.exclude.add("自摸")
        rf.exclude.add("门前清")
    # 和绝张: 和牌池、桌面已亮明的第四张牌
    if "和绝张" not in rf.exclude and "和绝张" in winning_condition:
        rf.fan_names.append("和绝张")
        rf.total_fan += 4
    # 门前清
    if "门前清" not in rf.exclude and (
        fan.men_qian_qing(history) and "自摸" in winning_condition
    ):
        rf.fan_names.append("门前清")
        rf.total_fan += 2
        rf.exclude.add("自摸")
    # 边张、坎张、单骑对子
    if "自摸" not in winning_condition:
        merged_suites = get_suites(tiles, shang_history)
        if "单骑对子" not in rf.exclude and "单骑对子" in winning_condition:
            rf.fan_names.append("单骑对子")
            rf.total_fan += 1
        if fan.bian_du(merged_suites, history):
            rf.fan_names.append("边张")
            rf.total_fan += 1
        if fan.kan_zhang(merged_suites, history):
            rf.fan_names.append("坎张")
            rf.total_fan += 1
    # 自摸
    if "自摸" not in rf.exclude and "自摸" in winning_condition:
        rf.fan_names.append("自摸")
        rf.total_fan += 1


def calculate_attribute_fan(
    rf: ResultFan,
    tiles,
    peng_history,
    gang_history,
    shang_history,
    an_gang_history,
    jiangs,
):
    # might want to pass in a copy of full_tiles instead for decoupled testing
    full_tiles = tiles + peng_history + gang_history + shang_history + an_gang_history
    distinct_tiles = get_distinct_tiles(full_tiles)
    merged_suites = get_suites(full_tiles)
    is_zu_he_long, ref = fan.zu_he_long(merged_suites)

    if not is_zu_he_long:
        if fan.lv_yi_se(full_tiles):
            rf.fan_names.append("绿一色")
            rf.total_fan += 88
            rf.exclude.update(["混一色"])
        if fan.jiu_lian_bao_deng(merged_suites, full_tiles):
            rf.fan_names.append("九莲宝灯")
            rf.total_fan += 88
            rf.exclude.update(["清一色", "不求人", "门前清", "无字", "幺九刻"])
        if fan.qing_yao_jiu(full_tiles):
            rf.fan_names.append("清幺九")
            rf.total_fan += 64
            rf.exclude.update(["混幺九", "碰碰和", "全带幺", "双同刻", "幺九刻", "无字"])
        if fan.zi_yi_se(full_tiles):
            rf.fan_names.append("字一色")
            rf.total_fan += 64
            rf.exclude.update(["混幺九", "碰碰和", "全带幺", "幺九刻"])
        if "混幺九" not in rf.exclude and fan.hun_yao_jiu(full_tiles):
            rf.fan_names.append("混幺九")
            rf.total_fan += 32
            rf.exclude.update(["幺九刻", "碰碰和", "全带幺"])
        if fan.quan_shuang_ke(full_tiles):
            rf.fan_names.append("全双刻")
            rf.total_fan += 24
            rf.exclude.update(["碰碰和", "断幺", "无字"])
        if "清一色" not in rf.exclude and fan.qing_yi_se(full_tiles, merged_suites):
            rf.fan_names.append("清一色")
            rf.total_fan += 24
            rf.exclude.update(["无字"])
        if fan.quan_da(full_tiles):
            rf.fan_names.append("全大")
            rf.total_fan += 24
            rf.exclude.update(["大于五", "无字"])
        if fan.quan_zhong(full_tiles):
            rf.fan_names.append("全中")
            rf.total_fan += 24
            rf.exclude.update(["断幺", "无字"])
        if fan.quan_xiao(full_tiles):
            rf.fan_names.append("全小")
            rf.total_fan += 24
            rf.exclude.update(["小于五", "无字"])
        if fan.quan_dai_wu(
            tiles,
            distinct_tiles,
            peng_history,
            gang_history,
            an_gang_history,
            shang_history,
            jiangs,
        ):
            rf.fan_names.append("全带五")
            rf.total_fan += 16
            rf.exclude.update(["断幺", "无字"])
        if "大于五" not in rf.exclude and fan.da_yu_wu(full_tiles):
            rf.fan_names.append("大于五")
            rf.total_fan += 12
            rf.exclude.update(["无字"])
        if "小于五" not in rf.exclude and fan.xiao_yu_wu(full_tiles):
            rf.fan_names.append("小于五")
            rf.total_fan += 12
            rf.exclude.update(["无字"])
        if fan.tui_bu_dao(full_tiles):
            rf.fan_names.append("推不倒")
            rf.total_fan += 8
            rf.exclude.update(["缺一门"])
        if "碰碰和" not in rf.exclude and fan.peng_peng_hu(distinct_tiles):
            rf.fan_names.append("碰碰和")
            rf.total_fan += 6
        if "混一色" not in rf.exclude and fan.hun_yi_se(merged_suites, full_tiles):
            rf.fan_names.append("混一色")
            rf.total_fan += 6
        if "全带幺" not in rf.exclude and fan.quan_dai_yao(
            tiles,
            distinct_tiles,
            peng_history,
            gang_history,
            an_gang_history,
            shang_history,
            jiangs,
        ):
            rf.fan_names.append("全带幺")
            rf.total_fan += 4
        if "断幺" not in rf.exclude and fan.duan_yao(full_tiles):
            rf.fan_names.append("断幺")
            rf.total_fan += 2
            rf.exclude.update(["无字"])
        if "缺一门" not in rf.exclude and fan.que_yi_men(merged_suites):
            rf.fan_names.append("缺一门")
            rf.total_fan += 1
    if fan.wu_men_qi(merged_suites, distinct_tiles):
        rf.fan_names.append("五门齐")
        rf.total_fan += 6
    if fan.ping_hu(
        full_tiles, peng_history, gang_history, an_gang_history, merged_suites
    ):
        rf.fan_names.append("平和")
        rf.total_fan += 2
        rf.exclude.update(["无字"])
    total_si_gui_yi = fan.si_gui_yi(distinct_tiles, gang_history, an_gang_history)
    if total_si_gui_yi:
        rf.fan_names.append("四归一")
        rf.total_fan += 2 * total_si_gui_yi
    if "无字" not in rf.exclude and fan.wu_zi(full_tiles):
        rf.fan_names.append("无字")
        rf.total_fan += 1


def calculate_ke_gang_fan(
    rf: ResultFan,
    tiles,
    gang_history,
    an_gang_history,
    jiangs,
):
    """
    四杠 88、四暗刻 64、三杠 32、三暗刻 16、双暗杠 6、双明杠 4、双暗刻 2、暗杠 2、明杠 1、明暗杠 5
    双暗杠 exclude 双暗刻
    四暗刻 exclude 碰碰和 不求人 门前清
    四杠 exclude 碰碰和 单骑对子
    """
    distinct_tiles = get_distinct_tiles(tiles)
    an_gang_cnt = len(an_gang_history) // 4
    gang_cnt = len(gang_history) // 4
    an_ke_cnt = 0
    for tile, cnt in distinct_tiles.items():
        if tile == jiangs:
            cnt -= 2
        # BUG tile cnt can be 2/3/4 and might or not might not be part of shang
        if cnt == 4 and check_shang(tile, tiles, jiangs):
            cnt -= 1
        if cnt == 3:
            an_ke_cnt += 1
    condition = an_gang_cnt * 100 + gang_cnt * 10 + an_ke_cnt
    if condition == 400:
        rf.fan_names.append("四杠")
        rf.total_fan += 88
        rf.exclude.update(["碰碰和", "单骑对子"])
        rf.fan_names.append("四暗刻")
        rf.total_fan += 64
        rf.exclude.update(["碰碰和", "不求人", "门前清"])
    elif condition == 310:
        rf.fan_names.append("四杠")
        rf.total_fan += 88
        rf.exclude.update(["碰碰和", "单骑对子"])
        rf.fan_names.append("三暗刻")
        rf.total_fan += 16
    elif condition == 220:
        rf.fan_names.append("四杠")
        rf.total_fan += 88
        rf.exclude.update(["碰碰和", "单骑对子"])
        rf.fan_names.append("双暗刻")
        rf.total_fan += 2
    elif condition == 130:
        rf.fan_names.append("四杠")
        rf.total_fan += 88
    elif condition == 301:
        rf.fan_names.append("三杠")
        rf.total_fan += 32
        rf.fan_names.append("四暗刻")
        rf.total_fan += 64
        rf.exclude.update(["碰碰和", "不求人", "门前清"])
    elif condition == 300:
        rf.fan_names.append("三杠")
        rf.total_fan += 32
        rf.fan_names.append("三暗刻")
        rf.total_fan += 16
    elif condition == 211:
        rf.fan_names.append("三杠")
        rf.total_fan += 32
        rf.fan_names.append("三暗刻")
        rf.total_fan += 16
    elif condition == 210:
        rf.fan_names.append("三杠")
        rf.total_fan += 32
        rf.fan_names.append("双暗刻")
        rf.total_fan += 2
    elif condition == 121:
        rf.fan_names.append("三杠")
        rf.total_fan += 32
        rf.fan_names.append("双暗刻")
        rf.total_fan += 2
    elif condition == 120:
        rf.fan_names.append("三杠")
        rf.total_fan += 32
    elif condition == 202:
        rf.fan_names.append("双暗杠")
        rf.total_fan += 6
        rf.fan_names.append("四暗刻")
        rf.total_fan += 64
        rf.exclude.update(["碰碰和", "不求人", "门前清"])
    elif condition == 201:
        rf.fan_names.append("双暗杠")
        rf.total_fan += 6
        rf.fan_names.append("三暗刻")
        rf.total_fan += 16
    elif condition == 112:
        rf.fan_names.append("明暗杠")
        rf.total_fan += 5
        rf.fan_names.append("三暗刻")
        rf.total_fan += 16
    elif condition == 111:
        rf.fan_names.append("明暗杠")
        rf.total_fan += 5
        rf.fan_names.append("双暗刻")
        rf.total_fan += 2
    elif condition == 22:
        rf.fan_names.append("双明杠")
        rf.total_fan += 4
        rf.fan_names.append("双暗刻")
        rf.total_fan += 2
    elif condition == 103:
        rf.fan_names.append("暗杠")
        rf.total_fan += 2
        rf.fan_names.append("四暗刻")
        rf.total_fan += 64
        rf.exclude.update(["碰碰和", "不求人", "门前清"])
    elif condition == 102:
        rf.fan_names.append("暗杠")
        rf.total_fan += 2
        rf.fan_names.append("三暗刻")
        rf.total_fan += 16
    elif condition == 101:
        rf.fan_names.append("暗杠")
        rf.total_fan += 2
        rf.fan_names.append("双暗刻")
        rf.total_fan += 2
    elif condition == 13:
        rf.fan_names.append("明杠")
        rf.total_fan += 1
        rf.fan_names.append("三暗刻")
        rf.total_fan += 16
    elif condition == 12:
        rf.fan_names.append("明杠")
        rf.total_fan += 1
        rf.fan_names.append("双暗刻")
        rf.total_fan += 2
    elif condition == 110:
        rf.fan_names.append("明暗杠")
        rf.total_fan += 5
    elif condition == 40:
        rf.fan_names.append("四杠")
        rf.total_fan += 88
        rf.exclude.update(["碰碰和", "单骑对子"])
    elif condition == 4:
        rf.fan_names.append("四暗刻")
        rf.total_fan += 64
        rf.exclude.update(["碰碰和", "不求人", "门前清"])
    elif condition == 30:
        rf.fan_names.append("三杠")
        rf.total_fan += 32
    elif condition == 3:
        rf.fan_names.append("三暗刻")
        rf.total_fan += 16
    elif condition == 200:
        rf.fan_names.append("双暗杠")
        rf.total_fan += 6
    elif condition == 20:
        rf.fan_names.append("双明杠")
        rf.total_fan += 4
    elif condition == 2:
        rf.fan_names.append("双暗刻")
        rf.total_fan += 2
    elif condition == 10:
        rf.fan_names.append("明杠")
        rf.total_fan += 1
    elif condition == 100:
        rf.fan_names.append("暗杠")
        rf.total_fan += 2


def calculate_feng_ke_fan(rf: ResultFan, distinct_tiles: dict):
    feng_ke = 0
    feng_jiang = 0
    for feng in FENGS:
        if distinct_tiles.get(feng, 0) >= 3:
            feng_ke += 1
        if distinct_tiles.get(feng, 0) == 2:
            feng_jiang += 1
    condition = feng_ke * 10 + feng_jiang
    if condition == 40:
        rf.fan_names.append("大四喜")
        rf.total_fan += 88
        rf.exclude.update(["圈风刻", "门风刻", "三风刻", "碰碰和"])
    elif condition == 31:
        rf.fan_names.append("小四喜")
        rf.total_fan += 64
        rf.exclude.update(["三风刻", "幺九刻"])
    elif condition == 30:
        rf.fan_names.append("三风刻")
        rf.total_fan += 12


def calculate_jian_ke_fan(rf: ResultFan, distinct_tiles: dict):
    jian_ke = 0
    jian_jiang = 0
    for jian in JIANS:
        if distinct_tiles.get(jian, 0) >= 3:
            jian_ke += 1
        if distinct_tiles.get(jian, 0) == 2:
            jian_jiang += 1
    condition = jian_ke * 10 + jian_jiang
    if condition == 30:
        rf.fan_names.append("大三元")
        rf.total_fan += 88
        rf.exclude.update(["双箭刻", "箭刻"])
    elif condition == 21:
        rf.fan_names.append("小三元")
        rf.total_fan += 64
        rf.exclude.update(["双箭刻", "箭刻"])
    elif condition == 20:
        rf.fan_names.append("双箭刻")
        rf.total_fan += 6
        rf.exclude.update(["箭刻"])


def calculate_tong_ke_fan(rf: ResultFan, distinct_tiles: dict):
    ke_holder = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
    }
    for k, v in distinct_tiles.items():
        if v >= 3:
            ke_holder[k[0]] += 1
    for v in ke_holder.values():
        if v == 3:
            rf.fan_names.append("三同刻")
            rf.total_fan += 16
        if v == 2 and "双同刻" not in rf.exclude:
            if "双同刻" not in rf.fan_names:
                rf.fan_names.append("双同刻")
            rf.total_fan += 2


def calculate_shang_fan(rf: ResultFan, tiles: list, shang_history: list):
    shang_sets = []
    tiles = sorted(tiles)
    for s in SUITES:
        distinct_tiles = {}
        for tile in tiles:
            if tile.endswith(s):
                if tile not in distinct_tiles:
                    distinct_tiles[tile[:-1]] = 1
                else:
                    distinct_tiles[tile[:-1]] += 1
        for group in SHANG_REF:
            if all([x in distinct_tiles for x in group]):
                candidates = []
                for x in group:
                    candidates.append(x)
                shang_sets.append([f"{x}{s}" for x in candidates])
    shang_sets = sorted(shang_sets.append(shang_history))
    if not shang_sets or len(shang_sets) == 1:
        return

    first_set_start = shang_sets[0][0][0]
    first_set_suite = shang_sets[0][0][1]
    second_set_start = shang_sets[1][0][0]
    second_set_suite = shang_sets[1][0][1]
    third_set_start = -1
    third_set_suite = ""
    fourth_set_start = -1
    fourth_set_suite = ""

    if len(shang_sets) == 3:
        third_set_start = shang_sets[2][0][0]
        third_set_suite = shang_sets[2][0][1]
        has_third_set = True
    if len(shang_sets) == 4:
        fourth_set_start = shang_sets[3][0][0]
        fourth_set_suite = shang_sets[3][0][1]
        has_fourth_set = True

    pair_suite_condition_map = {
        "12": first_set_suite == second_set_suite,
        "13": first_set_suite == third_set_suite,
        "14": first_set_suite == fourth_set_suite,
        "23": second_set_suite == third_set_suite,
        "24": second_set_suite == fourth_set_suite,
        "34": third_set_suite == fourth_set_suite,
    }
    pair_start_condition_map = {
        "12": abs(int(first_set_start) - int(second_set_start)),
        "13": abs(int(first_set_start) - int(third_set_start)),
        "14": abs(int(first_set_start) - int(fourth_set_start)),
        "23": abs(int(second_set_start) - int(third_set_start)),
        "24": abs(int(second_set_start) - int(fourth_set_start)),
        "34": abs(int(third_set_start) - int(fourth_set_start)),
    }

    max_paired_same_suites = sum(pair_suite_condition_map.values())
    if max_paired_same_suites == 4:
        if sum(pair_start_condition_map.values()) == 0:
            rf.fan_names.append("一色四同顺")
            rf.total_fan += 48
            rf.exclude.update(["一色三节高", "一般高", "四归一", "七对", "四归一", "一般高"])
        elif (
            sum(pair_start_condition_map.values()) == 20
            or sum(pair_start_condition_map.values()) == 10
        ):
            rf.fan_names.append("一色四步高")
            rf.total_fan += 32
            rf.exclude.update(["连六", "老少副"])
    keys = [k for k, v in pair_suite_condition_map.items() if v]
    sum_pair_start_condition_map = sum([pair_start_condition_map[k] for k in keys])
    # bring max_paired_same_suites out as first check then check sum_pair_start_condition_map
    if sum_pair_start_condition_map == 0:
        if max_paired_same_suites == 3:
            rf.fan_names.append("一色三同顺")
            rf.total_fan += 24
            rf.exclude.update(["一色三节高", "一般高"])
        elif max_paired_same_suites == 2:
            rf.fan_names.append("一般高x2")
            rf.total_fan += 2
        elif max_paired_same_suites == 1:
            rf.fan_names.append("一般高x2")
            rf.total_fan += 2
    elif max_paired_same_suites == 3 and (
        sum_pair_start_condition_map == 4 or sum_pair_start_condition_map == 8
    ):
        rf.fan_names.append("一色三步高")
        rf.total_fan += 16
    elif sum_pair_start_condition_map != 0 and max_paired_same_suites == 2:
        rf.fan_names.append("一般高")
        rf.total_fan += 1

    consider = {["12", "23", "13"]}
    if has_fourth_set:
        consider.update([["13", "34", "14"], ["14", "24", "12"], ["23", "34", "24"]])

    if max_paired_same_suites >= 3:
        for comb in consider:
            sum_pair_start_condition_map = sum(
                [pair_start_condition_map[k] for k in comb]
            )
            if sum_pair_start_condition_map == 12:
                rf.fan_names.append("清龙")
                rf.total_fan += 16
                rf.exclude.update(["连六", "老少副"])

    if has_third_set:
        for comb in consider:
            if (
                (not pair_suite_condition_map[comb[0]])
                and (not pair_suite_condition_map[comb[1]])
                and (not pair_suite_condition_map[comb[2]])
            ):
                sum_pair_start_condition_map = sum(
                    [pair_start_condition_map[k] for k in comb]
                )
                if sum_pair_start_condition_map == 0:
                    rf.fan_names.append("三色三同顺")
                    rf.total_fan += 8
                    rf.exclude.update(["喜相逢"])
                elif sum_pair_start_condition_map == 4:
                    rf.fan_names.append("三色三步高")
                    rf.total_fan += 6
                elif sum_pair_start_condition_map == 12:
                    rf.fan_names.append("花龙")
                    rf.total_fan += 8
    # xi_xiang_feng
    if "喜相逢" in rf.exclude:
        return

    consider = {"12"}
    if has_third_set:
        consider.update(["13"])
        if has_fourth_set:
            consider.update(["14", "24", "34"])
    for comb in consider:
        if not pair_suite_condition_map[comb]:
            if "喜相逢" not in rf.fan_names:
                rf.fan_names.append("喜相逢")
            rf.total_fan += 1


def calculate_associated_combination_fan(
    rf: ResultFan,
    tiles,
    peng_history,
    gang_history,
    shang_history,
    an_gang_history,
):
    """
    大四喜、大三元、小四喜、小三元、一色双龙会、一色四同顺、一色四节高、一色四步高、一色三同顺、
    一色三节高、清龙、三色双龙会、一色三步高、三同刻、三风刻、花龙、三色三同顺、三色三节高
    三色三步高、双箭刻、双同刻、一般高、喜相逢、连六、老少副
    tiles should be after removing zu_he_long?
    to consider if *_history should be included in each calculation
    """
    # tmp_rf = ResultFan()
    full_tiles = tiles + peng_history + gang_history + shang_history + an_gang_history
    distinct_tiles = get_distinct_tiles(full_tiles)

    calculate_feng_ke_fan(rf, distinct_tiles)
    calculate_jian_ke_fan(rf, distinct_tiles)

    # full tiles can be used?
    full_tiles = tiles + shang_history
    merged_suites = get_suites(full_tiles)
    if fan.yi_se_shuang_long_hui(merged_suites):
        rf.fan_names.append("一色双龙会")
        rf.total_fan += 64
        rf.exclude.update(["七对", "清一色", "平和", "一般高", "老少副", "无字"])
    if fan.san_se_shuang_long_hui(merged_suites):
        rf.fan_names.append("三色双龙会")
        rf.total_fan += 16
        rf.exclude.update(["喜相逢", "老少副", "无字", "平和"])

    full_tiles = tiles + peng_history + gang_history + an_gang_history
    merged_suites = get_suites(full_tiles)
    if fan.yi_se_si_jie_gao(merged_suites):
        rf.fan_names.append("一色四节高")
        rf.total_fan += 48
        rf.exclude.update(["一色三同顺", "一色三节高", "碰碰和"])
    if "一色三节高" not in rf.exclude and fan.yi_se_san_jie_gao(merged_suites):
        rf.fan_names.append("一色三节高")
        rf.total_fan += 24
        rf.exclude.update(["一色三同顺"])
    if fan.san_se_san_jie_gao(merged_suites):
        rf.fan_names.append("三色三节高")
        rf.total_fan += 12

    calculate_shang_fan(rf, tiles, shang_history)
    full_tiles = tiles + peng_history + gang_history + an_gang_history
    calculate_tong_ke_fan(rf, get_distinct_tiles(full_tiles))

    # 连六、老少副
    full_tiles = tiles + shang_history
    merged_suites = get_suites(full_tiles)
    lian_liu_cnt = fan.lian_liu(merged_suites)
    if lian_liu_cnt and "连六" not in rf.exclude:
        rf.fan_names.append("连六")
        rf.total_fan += lian_liu_cnt
    lao_shao_fu_cnt = fan.lao_shao_fu(merged_suites)
    if lao_shao_fu_cnt and "老少副" not in rf.exclude:
        rf.fan_names.append("老少副")
        rf.total_fan += lao_shao_fu_cnt
    # resolve conflicts?


def calculate_single_pack_fan(
    rf: ResultFan,
    tiles,
    peng_history,
    gang_history,
    an_gang_history,
    player_wind,
    round_wind,
):
    # 箭刻、圈风刻、门风刻、幺九刻
    full_tiles = tiles + peng_history + gang_history + an_gang_history
    distinct_tiles = get_distinct_tiles(full_tiles)
    if "箭刻" not in rf.exclude and fan.jian_ke(full_tiles):
        rf.fan_names.append("箭刻")
        rf.total_fan += 2
    if "圈风刻" not in rf.exclude and fan.quan_feng_ke(distinct_tiles, round_wind):
        rf.fan_names.append("圈风刻")
        rf.total_fan += 2
    if "门风刻" not in rf.exclude and fan.men_feng_ke(distinct_tiles, player_wind):
        rf.fan_names.append("门风刻")
        rf.total_fan += 2
    total_yao_jiu_ke = fan.yao_jiu_ke(distinct_tiles)
    if "幺九刻" not in rf.exclude and total_yao_jiu_ke:
        rf.fan_names.append("幺九刻")
        rf.total_fan += total_yao_jiu_ke


def check_qi_dui_hu(distinct_tiles: dict):
    return all([x == 2 for x in distinct_tiles.values()])


def calculate_fan(
    rf: ResultFan,
    winning_condition,
    history,
    tiles,
    peng_history,
    gang_history,
    shang_history,
    an_gang_history,
    flower_tiles,
    jiangs,
    round_wind="东",  # BUG until implemention
    player_wind="东",  # BUG until implemention
):
    """
    known bugs
    - when no peng/gang/shang, jiangs can be counted as ke
    - resolve pengs and shangs overlap
    """

    distinct_tiles = get_distinct_tiles(tiles)
    if fan.shi_san_yao(tiles):
        rf.fan_names.append("十三幺")
        rf.total_fan += 88
        rf.exclude.update(["混幺九", "五门齐", "不求人", "门前清", "单骑对子"])
    is_quan_bu_kao = fan.quan_bu_kao(distinct_tiles, get_suites(tiles))
    if is_quan_bu_kao:
        if fan.qi_xing_bu_kao(distinct_tiles, get_suites(tiles)):
            rf.fan_names.append("七星不靠")
            rf.total_fan += 24
            rf.exclude.update(["全不靠", "五门齐", "不求人", "门前清"])
        else:
            rf.fan_names.append("全不靠")
            rf.total_fan += 12
            rf.exclude.update(["五门齐", "不求人", "门前清"])
        is_zu_he_long, _ = fan.zu_he_long(get_suites(tiles))
        if is_zu_he_long:
            rf.fan_names.append("组合龙")
            rf.total_fan += 12

    if check_qi_dui_hu(distinct_tiles):
        if fan.lian_qi_dui(tiles):
            rf.fan_names.append("连七对")
            rf.total_fan += 88
            rf.exclude.update(["七对", "清一色", "不求人", "门前清", "无字", "单骑对子"])
        if "七对" not in rf.exclude and fan.qi_dui(distinct_tiles):
            rf.fan_names.append("七对")
            rf.total_fan += 24
            rf.exclude.update(["不求人", "门前清", "单骑对子"])
        calculate_attribute_fan(
            rf,
            winning_condition,
            history,
            tiles,
            peng_history,
            gang_history,
            shang_history,
            an_gang_history,
        )

    is_zu_he_long, ref = fan.zu_he_long(get_suites(tiles))
    if is_zu_he_long:
        tiles = remove_zu_he_long(tiles, ref)
    if is_zu_he_long and not is_quan_bu_kao:
        pass
    else:
        calculate_attribute_fan(
            rf,
            tiles,
            peng_history,
            gang_history,
            shang_history,
            an_gang_history,
            jiangs,
        )
        calculate_ke_gang_fan(
            rf,
            tiles,
            gang_history,
            an_gang_history,
        )  # BUG use get_valid_peng/gang on tiles
        calculate_associated_combination_fan(
            rf,
            tiles,
            peng_history,
            gang_history,
            shang_history,
            an_gang_history,
        )
        calculate_single_pack_fan(
            rf,
            tiles,
            peng_history,
            gang_history,
            an_gang_history,
            player_wind,
            round_wind,
        )

    calculate_win_mode_fan(
        rf,
        winning_condition,
        history,
        tiles,
        peng_history,
        gang_history,
        shang_history,
        an_gang_history,
    )

    if not rf.fan_names:
        rf.fan_names.append("无番和")
        rf.total_fan += 8

    # 每花1番。花牌补花成和计自摸，不计杠上开花
    if flower_tiles:
        rf.fan_names.append("花牌")
        rf.total_fan += len(flower_tiles)

    assert rf.total_fan > 0  # pragma: no cover; for brute force testing
    assert rf.total_fan <= 332  # pragma: no cover; for brute force testing
