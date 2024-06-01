from tiles import (
    FENGS,
    JIANS,
    SHANGS,
)

# -------- 1番 --------


def kan_zhang(merged_suites, history):
    # 4556(5)计，45567(6)不计
    # 只听一张牌，等待这张牌的胡牌形式只有一种
    if f"{len(history)}-hu-jiang-add" not in history:
        return False
    hu_tile = history[f"{len(history)}-hu-jiang-add"]
    if len(hu_tile) == 1:
        return False
    num, suite = hu_tile[0], hu_tile[1]
    if int(num) < 2 or int(num) > 8:
        return False
    pattern = f"{int(num) - 1}{num}{num}{num}{int(num) + 1}"
    if pattern in "".join(merged_suites[suite]):
        return True
    return False


def bian_du(merged_suites, history):
    # 12(3)，1233(3)，(7)89，(7)7789计
    # 12345(3)，56789(7) 不计
    # 只听一张牌，等待这张牌的胡牌形式只有一种
    if f"{len(history)}-hu-shang-add" not in history:
        return False
    hu_tile = history[f"{len(history)}-hu-shang-add"]
    if len(hu_tile) == 1:
        return False
    num, suite = hu_tile[0], hu_tile[1]
    joined = "".join(merged_suites[suite])
    if "5" in joined:
        return False
    # BUG below is not optimal
    if num == "3":
        if "123" in joined or "112233" in joined:
            return True
    if num == "7":
        if "789" in joined or "778899" in joined:
            return True
    return False


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
    return False


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
    return False


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
    return False


def si_gui_yi(tiles):
    # 4x same tile without gang
    # for each count 1
    return False


def ping_hu(tiles):
    # 四副顺子及序数牌。边，坎，单调将不影响。不计无字牌
    # cal_wu_zi = False
    return False


def men_qian_qing(history):
    # 没吃，碰，明杠。和他家出的牌
    for entry in history:
        if (
            "shang" in entry
            or "peng" in entry
            or "ming_gang" in entry
            or "jia_gang" in entry
        ):
            return False
    return True


def men_feng_ke(tiles):
    # 与自家本局相同的风刻
    # cal_yao_jiu_ke = False for this tile
    return False


def quan_feng_ke(tiles):
    # 与圈风相同的风刻
    # cal_yao_jiu_ke = False for this tile
    return False


def jian_ke(tiles):
    # 中，发，白的刻子
    # cal_yao_jiu_ke = False for this tile
    return False


# -------- 4番 --------


def shuang_ming_gang(history, gang_history):
    # 2x ming gang (strictly 2x)
    # if 1 ming 1 an => 5番
    if len(gang_history) != 8:
        return False
    ming_gang_ctr = 0
    for action in history:
        if "ming-gang-move" in action or "jia-gang-move" in action:
            ming_gang_ctr += 1
    return ming_gang_ctr == 2


def bu_qiu_ren(history, gang_history, peng_history, shang_history):
    """没碰，明杠，吃，自摸和牌"""
    if gang_history or peng_history or shang_history:
        return False
    if f"{len(history)}-hu-add-add" in history:  # BUG no more hu-add-add
        return False
    return True


def quan_dai_yao(tiles):
    # 每副顺子、刻子、将牌都有幺九牌
    return False


# -------- 6番 --------


def shuang_jian_ke(tiles):
    # 2x jian ke
    # cal_jian_ke = False for the two tiles
    return False


def shuang_an_gang(an_gang_history):
    # 2x an gang
    # cal_shuang_an_ke = False for the two tiles
    return (len(an_gang_history) / 4) == 2


def quan_qiu_ren(tiles: list, an_gang_history, history):
    # 吃，碰，明杠x4，和他家的牌
    # BUG hu-add-add tile can be more than 2
    if an_gang_history:
        return False
    if len(tiles) != 2:
        return False
    hu_key = f"{len(history)}-hu-add-add"  # BUG no more hu-add-add
    if (hu_key in history) and (history[hu_key]) == tiles[0]:
        return True
    return False


def wu_men_qi(merged_suites, distinct_tiles):
    # 和牌有索、筒、万、风、箭牌
    if len(merged_suites) != 3:
        return False
    feng_ctr = 0
    jian_ctr = 0
    for tile, count in distinct_tiles.items():
        if tile in FENGS:
            feng_ctr += 1
        if tile in JIANS:
            jian_ctr += 1
    if feng_ctr == 0 or jian_ctr == 0:
        return False
    return True


def san_se_san_bu_gao(tiles):
    # 三色三步高
    # 三种花色序数依次递增1的三幅顺子，123，234，345
    return False


def hun_yi_se(merged_suites: dict, tiles):
    # 混一色，由一种花色序数牌及字牌组成的和牌
    if len(merged_suites) != 1:
        return False
    suite = list(merged_suites.keys())[0]
    l = len(tiles) - len(merged_suites[suite])
    if l == 0:
        return False
    return True


def peng_peng_hu(distinct_tiles: dict):
    # 由四副刻子（或杠）组成的和牌
    # TODO can be checked earlier and just append `peng_peng_hu`?
    if len(distinct_tiles) != 5:
        return False
    set_ctr = 0
    for k, v in distinct_tiles.items():
        if v == 3 or v == 4:
            set_ctr += 1
    if set_ctr != 4:
        return False
    return True


# -------- 8番 --------


def wu_fan_he(tiles):
    # 和牌时，计算不出其他番种的和牌
    return False


def san_se_san_jie_gao(tiles):
    # 三色三节高
    # 三种花色依次递增1的三副刻子
    return False


def san_se_san_tong_shun(tiles):
    # 三色三同顺
    # 三种花色序数相同的三副顺子
    # cal_xi_xiang_feng = False
    return False


def tui_bu_dao(tiles):
    # 一、二、三、四、五、八、九筒
    # 二、四、五、六、八、九索
    # 白
    # 不计缺一门
    tong_candits = ("1筒", "2筒", "3筒", "4筒", "5筒", "8筒", "9筒")
    suo_candits = ("2索", "4索", "5索", "6索", "8索", "9索")
    for tile in tiles:
        if tile not in tong_candits + suo_candits + ("白",):
            return False
    return True


def hua_long(tiles):
    # 一种花色的123、第二种花色的456、第三种花色的789三副顺子
    return False


# -------- 12番 --------


def san_feng_ke(tiles):
    # 三风刻
    # cal_yao_jiu_ke = False for the three tiles
    return False


def xiao_yu_wu(tiles):
    # 由1234组成的和牌
    # cal_wu_zi = False
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[0] not in ("1", "2", "3", "4"):
            return False
    return True


def da_yu_wu(tiles):
    # 由6789组成的和牌
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[0] not in ("6", "7", "8", "9"):
            return False
    return True


def zu_he_long(merged_suites: dict):
    # to remove zu_he_long tiles for further processing
    # 一种花色的147、第二种花色的258、第三种花色的369的特殊顺子+将牌+1刻字
    ref = {}
    for suite, tiles in merged_suites.items():
        joined = "".join(tiles)
        if "1" in joined and "4" in joined and "7" in joined:
            ref[suite] = ["1", "4", "7"]
        if "2" in joined and "5" in joined and "8" in joined:
            ref[suite] = ["2", "5", "8"]
        if "3" in joined and "6" in joined and "9" in joined:
            ref[suite] = ["3", "6", "9"]
    return len(ref) == 3, ref


def quan_bu_kao(distinct_tiles: dict, merged_suites):
    # 东南西北中发白、147（索）、258（万）、369（饼）共16张牌中任意14张可胡
    # 这里索、万、饼位置可以互换
    # might want to slim down qi_xing_bu_kao by
    comb_1 = "147"
    comb_2 = "258"
    comb_3 = "369"
    ref = {}
    ctr = 0
    for suite, tiles in merged_suites.items():
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
            ctr += len(tiles)
            # for tile in tiles:
            #     tiles.remove(tile + suite)
        else:
            return False
    if len(ref) != 3:
        return False
    expected_zi = 14 - ctr
    zi_ctr = 0
    for tile, tile_cnt in distinct_tiles.items():
        if tile in FENGS + JIANS and tile_cnt == 1:
            zi_ctr += 1
    # commented portion seems to be implied
    # for tile in tiles:
    #     if tile not in FENGS + JIANS:
    #         return False
    return zi_ctr == expected_zi


# -------- 16番 --------


def san_an_ke(distinct_tiles, gang_history, peng_history):
    # 三暗刻/杠
    ke_ctr = 0
    for k, v in distinct_tiles.items():
        if v == 3 or v == 4:
            if k not in gang_history and k not in peng_history:
                ke_ctr += 1
    return ke_ctr == 3


def san_tong_ke(tiles):
    # 三同刻，三中花色序数相同的刻子
    # cal_shuang_tong_ke = False for the three tiles
    return False


def quan_dai_wu(tiles):
    # 每副顺子、刻子、将牌都有序数牌5
    ctr = 0
    for tile in tiles:
        if tile in FENGS + JIANS:
            return False
        if tile[0] == "5":
            ctr += 1
    return ctr >= 6


def yi_se_san_bu_gao(merged_suites: dict):
    # 一色三步高，由一种花色序数依次递增1或2的三副顺子组成的和牌
    # 123，234或123，345皆可
    for suite, tiles in merged_suites.items():
        if len(tiles) == 9:
            return True
    return False


def san_se_shuang_long_hui(merged_suites: dict):
    # 三色双龙会，三种花色，两种花色的两副老少副和第三种花色5的将牌
    # cal_ping_hu = False
    # cal_lao_shao_fu = False
    # cal_xi_xiang_feng = False
    # cal_wu_zi = False
    if len(merged_suites) != 3:
        return False
    lao_shao_fu_suite = []
    jiang_pai_suite = ""
    for suite, tiles in merged_suites.items():
        joined = "".join(tiles)
        if joined != "123789" and joined != "55":
            return False
        if joined == "123789":
            lao_shao_fu_suite.append(suite)
        if joined == "55":
            jiang_pai_suite = suite
    if jiang_pai_suite in lao_shao_fu_suite or len(lao_shao_fu_suite) != 2:
        return False
    return True


def qing_long(merged_suites: dict):
    # 一种花色的123，456，789的三副顺子
    # cal_lian_liu = False
    # cal_lao_shao_fu = False
    for suite, tiles in merged_suites.items():
        if "123456789" == "".join(tiles):
            return True
    return False


# -------- 24番 --------


def quan_xiao(tiles):
    # 由序数123组成的和牌
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[0] not in ("1", "2", "3"):
            return False
    return True


def quan_zhong(tiles):
    # 由序数456组成的和牌
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[0] not in ("4", "5", "6"):
            return False
    return True


def quan_da(tiles):
    # 由序数789组成的和牌
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
    return False


def yi_se_san_tong_shun(distinct_tiles, merged_suites: dict):
    # 一色三同顺，一种花色三副序数相同的顺子
    # 123, 123, 123
    # cal_san_se_san_bu_gao = False
    # cal_yi_ban_gao = False
    return False


def qing_yi_se(tiles, merged_suites):
    # 由一种花色的序数牌组成的和牌
    for tile in tiles:
        if len(tile) == 1:
            return False
    if len(merged_suites) != 1:
        return False
    return True


def quan_shuang_ke(tiles):
    # 由双序数牌（2，4，6，8）组成的刻子、将牌
    for tile in tiles:
        if len(tile) == 1:
            return False
        if tile[0] not in ("2", "4", "6", "8"):
            return False
    return True


def qi_xing_bu_kao(distinct_tiles, merged_suites: dict):
    # 由东南西北中发白，加上一种花色的147，另一种花色的258，第三种花色的369的七张牌组成的和牌
    # 特殊牌型
    # BUG 331 condition not considered
    if len(distinct_tiles) != 14:
        return False
    for tile in JIANS + FENGS:
        if tile not in distinct_tiles:
            return False
    comb_1 = "147"
    comb_2 = "258"
    comb_3 = "369"
    ref = {}
    for suite, tiles in merged_suites.items():
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
    return False


def yi_se_si_bu_gao(tiles):
    # 一色四步高，一种花色四副依次递增1，2的顺子
    # cal_san_se_san_bu_gao = False
    # cal_lian_liu = False
    # cal_lao_shao_fu = False
    return False


# -------- 48番 --------


def yi_se_si_jie_gao(merged_suites):
    # 一色四节高，一种花色四副依次递增1的刻子
    # cal_yi_se_san_tong_shun = False
    # cal_yi_se_san_jie_gao = False
    # cal_peng_peng_hu = False
    distinct = {}
    for tile in merged_suites:
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


def yi_se_si_tong_shun(merged_suites):
    # 一色四同顺，一种花色四副序数相同的顺子
    # cal_yi_se_san_tong_shun = False
    # cal_yi_se_san_jie_gao = False
    # cal_qi_dui = False
    # cal_si_gui_yi = False
    # cal_yi_ban_gao = False
    # assume suite is same and input is without eyes
    distinct = {}
    for tile in merged_suites:
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
    for tile in tiles:
        if tile not in JIANS + FENGS:
            return False
    return True


def xiao_san_yuan(tiles):
    # 小三元，中发白两副刻子第三副为将
    # cal_shuang_jian_ke = False
    # cal_jian_ke = False
    # cal_yao_jiu_ke = False for the two 刻子
    return False


def xiao_si_xi(tiles):
    # 小四喜，东南西北三副刻子第四副为将
    # cal_san_feng_ke = False
    # cal_yao_jiu_ke = False
    return False


def qing_yao_jiu(tiles):
    # 清幺九，和牌时全是幺九牌
    for tile in tiles:
        if tile[0] not in ("1", "9"):
            return False
    return True


# -------- 88番 --------


def shi_san_yao(tiles):
    # 十三幺，由一种花色的1、9序数牌和字牌组成的和牌
    ref = ["1万", "9万", "1筒", "9筒", "1索", "9索"] + list(FENGS) + list(JIANS)
    for r in ref:
        if sorted(tiles) == sorted(ref + [r]):
            return True
    return False


def lian_qi_dui(tiles):
    # 连七对，一个花色序数相连的七个对子成和牌
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
    return False


def da_si_xi(tiles):
    # 大四喜，东南西北四副刻子
    # cal_san_feng_ke = False
    # cal_peng_peng_hu = False
    # cal_quan_feng_ke = False
    # cal_men_feng_ke = False
    # cal_yao_jiu_ke = False
    return False