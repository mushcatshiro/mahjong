from tiles import (
    FENGS,
    JIANS,
    HUAS,
    SHANGS,
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


def count_feng_ke(tiles):
    cnt = 0
    for feng in FENGS:
        if feng in tiles:
            cnt += 1
    return cnt


def count_jian_ke(tiles):
    cnt = 0
    for jian in JIANS:
        if jian in tiles:
            cnt += 1
    return cnt


def count_hua(tiles):
    cnt = 0
    for hua in HUAS:
        if hua in tiles:
            cnt += 1
    return cnt


def has_feng_ke(tiles):
    # 3/4x of feng
    return False


def has_jian_ke(tiles):
    # 3x of jian
    return False


def get_suites(tiles, shang_history=[]):
    # BUG need to align across all fn calls
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
    for suite, tiles in ref.items():
        for tile in tiles:
            tiles.remove(tile + suite)
    return tiles


def calculate_win_mode_fan(
    rf: ResultFan,
    winning_condition: list,
    history,
    tiles,
    distinct_tiles,
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
    winning_condition: list,
    history,
    tiles,
    distinct_tiles,
    peng_history,
    gang_history,
    shang_history,
    an_gang_history,
):
    full_tiles = tiles + peng_history + gang_history + shang_history + an_gang_history
    merged_suites = get_suites(tiles, shang_history)

    if not fan.zu_he_long(full_tiles):
        if fan.lv_yi_se(full_tiles):
            rf.fan_names.append("绿一色")
            rf.total_fan += 88
            rf.exclude.update(["混一色"])
        if fan.jiu_lian_bao_deng(full_tiles):
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
        if "混一色" not in rf.exclude and hun_yi_se(merged_suites, full_tiles):
            rf.fan_names.append("混一色")
            rf.total_fan += 48
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
        if fan.quan_dai_wu(full_tiles):
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
        if "全带幺" not in rf.exclude and fan.quan_dai_yao(full_tiles):
            rf.fan_names.append("全带幺")
            rf.total_fan += 4
        if "断幺" not in rf.exclude and fan.duan_yao(full_tiles):
            rf.fan_names.append("断幺")
            rf.total_fan += 2
        if "缺一门" not in rf.exclude and fan.que_yi_men(full_tiles):
            rf.fan_names.append("缺一门")
            rf.total_fan += 1
    if fan.wu_men_qi(merged_suites, distinct_tiles):
        rf.fan_names.append("五门齐")
        rf.total_fan += 6
    if fan.ping_hu(full_tiles):
        rf.fan_names.append("平和")
        rf.total_fan += 2
        rf.exclude.update(["无字"])
    if fan.si_gui_yi(full_tiles):
        rf.fan_names.append("四归一")
        rf.total_fan += 2
    if "无字" not in rf.exclude and fan.wu_zi(full_tiles):
        rf.fan_names.append("无字")
        rf.total_fan += 1


def check_qi_dui(distinct_tiles: dict):
    return all([x == 2 for x in distinct_tiles.values()])


def check_zu_he_long():
    pass


def check_specials():
    # 十三幺 七星不靠 全不靠
    pass


def check_basic_hu():
    pass


def calculate_fan(
    rf: ResultFan,
    winning_condition,
    history,
    tiles,
    distinct_tiles,
    peng_history,
    gang_history,
    shang_history,
    an_gang_history,
    flower_tiles,
    round_wind=None,
    player_wind=None,
):
    if fan.shi_san_yao(tiles):
        rf.fan_names.append("十三幺")
        rf.total_fan += 88
        rf.exclude.update(["混幺九", "五门齐", "不求人", "门前清", "单骑对子"])
    is_quan_bu_kao = fan.quan_bu_kao(distinct_tiles, get_suites(tiles, shang_history))
    if is_quan_bu_kao:
        if fan.qi_xing_bu_kao():
            rf.fan_names.append("七星不靠")
            rf.total_fan += 24
            rf.exclude.update(["全不靠", "五门齐", "不求人", "门前清"])
        else:
            rf.fan_names.append("全不靠")
            rf.total_fan += 12
            rf.exclude.update(["五门齐", "不求人", "门前清"])
        is_zu_he_long, _ = fan.zu_he_long()  # BUG
        if is_zu_he_long:
            rf.fan_names.append("组合龙")
            rf.total_fan += 12

    if check_qi_dui(tiles):
        if fan.lian_qi_dui():
            rf.fan_names.append("连七对")
            rf.total_fan += 88
            rf.exclude.update(["七对", "清一色", "不求人", "门前清", "无字", "单骑对子"])
        if "七对" not in rf.exclude and fan.qi_dui():
            rf.fan_names.append("七对")
            rf.total_fan += 24
            rf.exclude.update(["不求人", "门前清", "单骑对子"])
        calculate_attribute_fan(
            rf,
            winning_condition,
            history,
            tiles,
            distinct_tiles,
            peng_history,
            gang_history,
            shang_history,
            an_gang_history,
        )

    is_zu_he_long, ref = fan.zu_he_long()  # BUG
    if is_zu_he_long:
        tiles = remove_zu_he_long(tiles, ref)
    if is_zu_he_long and not is_quan_bu_kao:
        # do something?
        pass
    else:
        dfs()

    calculate_win_mode_fan(
        rf,
        winning_condition,
        history,
        tiles,
        distinct_tiles,
        peng_history,
        gang_history,
        shang_history,
        an_gang_history,
    )

    # 每花1番。花牌补花成和计自摸，不计杠上开花
    if flower_tiles:
        rf.fan_names.append("花牌")
        rf.total_fan += len(flower_tiles)
