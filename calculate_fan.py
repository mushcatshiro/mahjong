from tiles import (
    FENGS,
    JIANS,
    HUAS,
    SHANGS,
)


class Fan:
    def __init__(self):
        self.total_fan = 0
        self.fan_names = []
        self.cal_wu_zi = True


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


def get_suites(tiles):
    # BUG need to align across all fn calls
    suites = {}
    for tile in tiles:
        if len(tile) == 2:
            if tile[1] not in suites:
                suites[tile[1]] = [tile[0]]
            else:
                suites[tile[1]].append(tile[0])
    return suites


# -------- 1番 --------


def hua_pai(flower_tiles):
    # 每花1番。花牌补花成和计自摸，不计杠上开花
    return len(flower_tiles)


def zi_mo(history):
    # TODO might be a convinient fn to have
    return history[-1][0] == "HU"


def dan_qi_dui_zi(distinct_tiles, history):
    # if drawed tile forms eye to hu
    # 只听一张牌，等待这张牌的胡牌形式只有一种
    if distinct_tiles[history[f"{len(history)}-hu-add"]] == 2:
        return True
    return False


def kan_zhang(tiles):
    # if drawed tile is in between two tiles and leads to hu
    # 4556, 5 is kan zhang
    # 45567, 6 is not
    # 只听一张牌，等待这张牌的胡牌形式只有一种
    pass


def bian_du(tiles, history):
    # 123 or 1233, 3 is bian du
    # 12345, 4 is not
    # 789 or 7899, 7 is bian du
    # 只听一张牌，等待这张牌的胡牌形式只有一种
    pass


def wu_zi(tiles):
    # if all tiles are numbered tiles
    for tile in tiles:
        if tile in FENGS or tile in JIANS:
            return False
    return True


def ming_gang(history):
    # allow both ming gang and jia gang
    for action in history:
        if "ming-gang-move" in action or "jia-gang-move" in action:
            return True
    return False


def que_yi_men(tiles):
    # has only two suits
    suite_ctr = set()
    for tile in tiles:
        if len(tile) == 2:
            suite_ctr.add(tile[1])
    return len(suite_ctr) == 2


def yao_jiu_ke(distinct_tiles):
    # 111, 999, 1111, 9999 and FENGS
    # for each count 1
    total_yao_jiu_ke = 0
    for k, v in distinct_tiles.items():
        if v == 3 and k in ("1万", "9万", "1筒", "9筒", "1索", "9索") + FENGS:
            total_yao_jiu_ke += 1
    return total_yao_jiu_ke


def lao_shao_fu(merged_suites: dict):
    # combine hand + shang history
    # 123 and 789 of a single suite
    # for each count 1
    total_lao_shao_fu = 0
    for suite in merged_suites.values():
        if ("1" in suite and "2" in suite and "3" in suite) and (
            "7" in suite and "8" in suite and "9" in suite
        ):
            total_lao_shao_fu += 1
    return total_lao_shao_fu


def lian_liu(suites: dict):
    # 一种花色的连续六张牌
    # for each count 1
    total_lian_liu = 0
    for tiles in suites.values():
        if len(tiles) >= 6:
            fptr = 0
            bptr = 6
            while bptr <= len(tiles):
                if int(tiles[fptr][0]) + 5 == int(tiles[fptr + 5][0]):
                    total_lian_liu += 1
                    fptr = bptr
                    bptr += 6
    return total_lian_liu


def xi_xiang_feng(merged_suites: dict):
    # BUG
    # 2 suites of same shang i.e. 123
    # for each count 1
    total_xi_xiang_feng = 0
    combi = {}
    for suite, tiles in merged_suites.items():
        for fptr in range(0, len(tiles), 3):
            grp = tiles[fptr : fptr + 3]
            if grp in SHANGS:
                if grp not in combi:
                    combi[grp] = 1
                else:
                    combi[grp] += 1

    pass


def yi_ban_gao(merged_suites: dict):
    # BUG
    # one suite 2x of shang
    # for each count 1
    total_yi_ban_gao = 0
    for suite, tiles in merged_suites.items():
        for fptr in range(0, len(tiles), 3):
            grp = tiles[fptr : fptr + 3]
            if grp in SHANGS:
                if tiles.count(grp) == 2:
                    total_yi_ban_gao += 1
    pass


# -------- 2番 --------


def duan_yao(tiles):
    # no 1, 9， FENGS, JIANS
    # cal_wu_zi = False
    for tile in tiles:
        if tile[0] in ("1", "9") + FENGS + JIANS:
            return False
    return True


def an_gang(distinct_tiles):
    total_an_gang = 0
    for k, v in distinct_tiles.items():
        if v == 4:
            total_an_gang += 1
    return total_an_gang


def shuang_an_ke(distinct_tiles):
    # 2x an ke or an gang
    ctr = 0
    for k, v in distinct_tiles.items():
        if v == 4 or v == 3:
            ctr += 1
    return ctr == 2


def shuang_tong_ke(tiles):
    # 2 suite of same ke
    # for each count 1
    pass


def si_gui_yi(tiles):
    # 4x same tile without gang
    # for each count 1
    pass


def ping_hu(tiles):
    # 四副顺子及序数牌。边，坎，单调将不影响。不计无字牌
    # cal_wu_zi = False
    pass


def men_qian_qing(history):
    # 没吃，碰，明杠。和他家出的牌
    # cal_zi_mo = False
    pass


def men_feng_ke(tiles):
    # 与自家本局相同的风刻
    # cal_yao_jiu_ke = False for this tile
    pass


def quan_feng_ke(tiles):
    # 与圈风相同的风刻
    # cal_yao_jiu_ke = False for this tile
    pass


def jian_ke(tiles):
    # 中，发，白的刻子
    # cal_yao_jiu_ke = False for this tile
    pass


# -------- 24番 --------


def quan_xiao(tiles):
    # 由序数123组成的和牌
    # cal_xiao_yu_wu = False
    # cal_wu_zi = False
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[0] not in ("1", "2", "3"):
            return False
    return True


def quan_zhong(tiles):
    # 由序数456组成的和牌
    # cal_duan_yao = False
    # cal_wu_zi = False
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[0] not in ("4", "5", "6"):
            return False
    return True


def quan_da(tiles):
    # 由序数789组成的和牌
    # cal_da_yu_wu = False
    # cal_wu_zi = False
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[0] not in ("7", "8", "9"):
            return False
    return True


def yi_se_san_jie_gao(tiles):
    # 一色三节高，一种花色三副依次递增1的刻子
    # 111, 222, 333
    # cal_yi_se_san_tong_shun = False
    pass


def yi_se_san_tong_shun(distinct_tiles, merged_suites_list: dict):
    # 一色三同顺，一种花色三副序数相同的顺子
    # 123, 123, 123
    # cal_san_se_san_bu_gao = False
    # cal_yi_ban_gao = False
    pass


def qing_yi_se(tiles, merged_suites_list):
    # 由一种花色的序数牌组成的和牌
    # cal_wu_zi = False
    for tile in tiles:
        if len(tile) == 1:
            return False
    if len(merged_suites_list) != 1:
        return False
    return True


def quan_shuang_ke(tiles):
    # 由双序数牌（2，4，6，8）组成的刻子、将牌
    # cal_peng_peng_hu = False
    # cal_duan_yao = False
    # cal_wu_zi = False
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[0] not in ("2", "4", "6", "8"):
            return False
    return True


def qi_xing_bu_kao(distinct_tiles, merged_suites_list: dict):
    # 由东南西北中发白，加上一种花色的147，另一种花色的258，第三种花色的369组成的和牌
    # 特殊牌型
    # cal_quan_bu_kao = False
    # cal_wu_men_qi = False
    # cal_bu_qiu_ren = False
    # cal_men_qian_qing = False
    if len(distinct_tiles) != 14:
        return False
    for tile in JIANS + FENGS:
        if tile not in distinct_tiles:
            return False
    comb_1 = "147"
    comb_2 = "258"
    comb_3 = "369"
    ref = {}
    for suite, tiles in merged_suites_list.items():
        joined = "".join(tiles)
        if (
            joined == comb_1
            or joined == comb_2
            or joined == comb_3
            or joined == comb_1[:-1]
            or joined == comb_2[:-1]
            or joined == comb_3[:-1]
            or joined == comb_1[1:]
            or joined == comb_2[1:]
            or joined == comb_3[1:]
        ):
            ref[suite] = joined
        else:
            return False
    if len(ref) != 3:
        return False
    return True


def qi_dui(distinct_tiles):
    # 七对，由7个对子组成的和牌
    # cal_dan_qi_dui_zi = False
    # cal_bu_qiu_ren = False
    # cal_men_qian_qing = False
    if len(distinct_tiles) != 7:
        return False
    return True


# -------- 32番 --------


def hun_yao_jiu(tiles):
    # 混幺九，由字牌和序数牌1、9组成的和牌
    # cal_yao_jiu_ke = False
    # cal_peng_peng_hu = False
    # cal_quan_dai_yao = False
    for tile in tiles:
        if len(tile) == 1:
            continue
        if tile[0] not in ("1", "9"):
            return False
    return True


def san_gang(tiles):
    # 三杠，和牌中有三个杠
    # 暗杠加计暗刻番
    pass


def yi_se_si_bu_gao(tiles):
    # 一色四步高，一种花色四副依次递增1，2的顺子
    # cal_san_se_san_bu_gao = False
    # cal_lian_liu = False
    # cal_lao_shao_fu = False
    pass


# -------- 48番 --------


def yi_se_si_jie_gao(merged_suites_list):
    # 一色四节高，一种花色四副依次递增1的刻子
    # cal_yi_se_san_tong_shun = False
    # cal_yi_se_san_jie_gao = False
    # cal_peng_peng_hu = False
    distinct = {}
    for tile in merged_suites_list:
        if tile not in distinct:
            distinct[tile] = 1
        else:
            distinct[tile] += 1
    if len(distinct) != 4:
        return False
    keys = [x[0] for x in list(distinct.keys())]
    if (
        int(keys[0]) + 1 == int(keys[1])
        and int(keys[1]) + 1 == int(keys[2])
        and int(keys[2]) + 1 == int(keys[3])
    ):
        return True
    return False


def yi_se_si_tong_shun(merged_suites_list):
    # 一色四同顺，一种花色四副序数相同的顺子
    # cal_yi_se_san_tong_shun = False
    # cal_yi_se_san_jie_gao = False
    # cal_qi_dui = False
    # cal_si_gui_yi = False
    # cal_yi_ban_gao = False
    # assume suite is same and input is without eyes
    distinct = {}
    for tile in merged_suites_list:
        if tile not in distinct:
            distinct[tile] = 1
        else:
            distinct[tile] += 1
    if len(distinct) != 3:
        return False
    keys = [x[0] for x in list(distinct.keys())]
    if int(keys[0]) + 1 == int(keys[1]) and int(keys[1]) + 1 == int(keys[2]):
        return True
    return False


# -------- 64番 --------


def yi_se_shuang_long_hui(tiles, distinct_tiles):
    # 一色双龙会，一种花色两副老少副和本花色5的将牌
    # cal_qi_dui = False
    # cal_qing_yi_se = False
    # cal_ping_hu = False
    # cal_lao_shao_fu = False
    # cal_yi_ban_gao = False
    # cal_wu_zi = False
    # based on `lao_shao_fu`, if rv == 2 then check yi_se_shuang_long_hui
    suite = tiles[0][1]
    if "5" + suite not in distinct_tiles or distinct_tiles["5" + suite] != 2:
        return False
    return True


def si_an_ke(distinct_tiles, gang_history):
    # 四暗刻，四个暗刻
    # cal_peng_peng_hu = False
    # cal_bu_qiu_ren = False
    # cal_men_qian_qing = False
    if gang_history:
        return False
    if len(distinct_tiles) != 4:
        return False
    for k, v in distinct_tiles.items():
        if v != 4:
            return False
    return True


def zi_yi_se(tiles):
    # 字一色，全部由字牌组成的和牌
    # cal_hun_yao_jiu = False
    # cal_peng_peng_hu = False
    # cal_quan_dai_yao = False
    # cal_yao_jiu_ke = False
    for tile in tiles:
        if tile not in JIANS + FENGS:
            return False
    return True


def xiao_san_yuan(tiles):
    # 小三元，中发白两副刻子第三副为将
    # cal_shuang_jian_ke = False
    # cal_jian_ke = False
    # cal_yao_jiu_ke = False for the two 刻子
    pass


def xiao_si_xi(tiles):
    # 小四喜，东南西北三副刻子第四副为将
    # cal_san_feng_ke = False
    # cal_yao_jiu_ke = False
    pass


def qing_yao_jiu(tiles):
    # 清幺九，和牌时全是幺九牌
    # cal_hun_yao_jiu = False
    # cal_peng_peng_hu = False
    # cal_quan_dai_yao = False
    # cal_shuang_tong_ke = False
    # cal_yao_jiu_ke = False
    # cal_wu_zi = False
    for tile in tiles:
        if tile[0] not in ("1", "9"):
            return False
    return True


# -------- 88番 --------


def shi_san_yao(tiles):
    # 十三幺，由一种花色的1、9序数牌和字牌组成的和牌
    # cal_hun_yao_jiu = False
    # cal_wu_men_qi = False
    # cal_bu_qiu_ren = False
    # cal_men_qian_qing = False
    # cal_dan_qi_dui_zi = False
    ref = ["1万", "9万", "1筒", "9筒", "1索", "9索"] + list(FENGS) + list(JIANS)
    for r in ref:
        if sorted(tiles) == sorted(ref + [r]):
            return True
    return False


def lian_qi_dui(tiles):
    # 连七对，一个花色序数相连的七个对子成和牌
    # cal_qing_yi_se = False
    # cal_qi_dui = False
    # cal_bu_qiu_ren = False
    # cal_men_qian_qing = False
    # cal_wu_zi = False
    # cal_dan_qi_dui_zi = False
    tiles = sorted(tiles)
    bptr = 0
    fptr = 1
    prev = -1
    while fptr < len(tiles):
        if tiles[fptr] in JIANS + FENGS or tiles[bptr] in JIANS + FENGS:
            return False
        if tiles[fptr] != tiles[bptr]:
            return False
        if fptr == 1:
            prev = tiles[fptr][0]
        else:
            if int(tiles[fptr][0]) - 1 != int(prev):
                return False
            prev = tiles[fptr][0]
        bptr += 2
        fptr += 2
    return True


def si_gang(distinct_tiles: dict, eyes):
    # 四杠，和牌中有四个杠，暗杠加计暗刻番
    # cal_peng_peng_hu = False
    # cal_dan_qi_dui_zi = False
    if len(distinct_tiles) != 5:
        return False
    for tile, count in distinct_tiles.items():
        if tile == eyes:
            continue
        if count != 4:
            return False
    return True


def jiu_lian_bao_deng(tiles):
    # 九莲宝灯，一种花色序数牌1112345678999+本花色任何牌成和牌
    # cal_qing_yi_se = False
    # cal_bu_qiu_ren = False
    # cal_men_qian_qing = False
    # cal_wu_zi = False
    # cal_yao_jiu_ke = False x1?
    suite = tiles[0][1]
    nums = [tile[0] for tile in tiles]
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[1] != suite:
            return False
    nums = sorted(nums)
    ref = ["1", "1", "1", "2", "3", "4", "5", "6", "7", "8", "9", "9", "9"]
    for i in range(1, 10):
        if nums == sorted(ref + [str(i)]):
            return True
    return False


def lv_yi_se(tiles):
    # 绿一色，由23468索及发财组成的和牌
    # cal_hun_yi_se = False
    # if no fa then cal_qing_yi_se = True
    for tile in tiles:
        if len(tile) == 1 and tile in FENGS + ("中", "白"):
            return False
        if tile == "發":
            continue
        if tile[1] in ("筒", "万"):
            return False
        if tile[0] in ("1", "5", "7", "9"):
            return False
    return True


def da_san_yuan(tiles):
    # 大三元，中发白三副刻子
    # cal_shang_jian_ke = False
    # cal_jian_ke = False
    # cal_yao_jiu_ke = False for the three 刻子
    pass


def da_si_xi(tiles):
    # 大四喜，东南西北四副刻子
    # cal_san_feng_ke = False
    # cal_peng_peng_hu = False
    # cal_quan_feng_ke = False
    # cal_men_feng_ke = False
    # cal_yao_jiu_ke = False
    return True


def calculate_fan(
    tiles, shang_history, peng_history, gang_history, history, round_wind, player_wind
):
    """ """
    total_fan = 0
    fan_name = []

    # TODO move to `PlayResult`?
    # check for 13幺、七星不靠、全不靠
    special_combi = check_specials(tiles)
    if special_combi:
        fan_name.append(special_combi)
        total_fan += FANMAP[special_combi]
        # 全不靠、七星不靠可复合组合龙
        # exclude 不求人、门前请
        # if 自摸

    # TODO move to `PlayResult`?
    # check for 七对、连七对

    if has_feng_ke(tiles):
        feng_ke_count = count_feng_ke(tiles)
        if feng_ke_count == 4:
            # 大四喜
            total_fan += 88
            cal_quan_feng_ke = False
            cal_men_feng_ke = False
            cal_peng_peng_hu = False
            cal_yao_jiu_ke = False
            # cal_san_feng_ke = False  # implied
        elif feng_ke_count == 3:
            if eye in FENGS:
                # 小四喜
                total_fan += 64
            else:
                # 三风刻
                pass
        else:
            # check men feng/quan feng
            total_fan += 2  # TODO for each

    if has_jian_ke(tiles):
        jian_ke_count = count_jian_ke(tiles)
        if jian_ke_count == 3:
            # 大三元
            total_fan += 88
        elif jian_ke_count == 2:
            if eye in JIANS:
                # 小三元
                total_fan += 64
            else:
                # 三风刻
                pass
        else:
            # 箭刻
            total_fan += 2  # TODO for each

    hua_count = count_hua(tiles)
    total_fan += hua_count * 1

    # 不求人
    if is_bu_qiu_ren(history):
        total_fan += 4
        check_zi_mo = False

    if check_zi_mo and is_zi_mo(history):
        total_fan += 1
