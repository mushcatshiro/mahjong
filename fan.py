from tiles import (
    FENGS,
    JIANS,
)

# -------- 1番 --------


def kan_zhang(merged_suites, history):
    # 46(5)，4556(5)计，45567(6)不计
    # 只听一张牌，等待这张牌的胡牌形式只有一种
    action = history[f"{len(history) - 1}"]["action"]
    play_action = history[f"{len(history) - 1}"]["play_action"]
    hu_tile = history[f"{len(history) - 1}"]["tile"]
    if action != "hu-add" and play_action != "shang":
        return False
    if len(hu_tile) == 1:
        return False
    num, suite = hu_tile[0], hu_tile[1]
    if int(num) < 2 or int(num) > 8:
        return False
    pattern_1 = f"{int(num) - 1}{num}{num}{num}{int(num) + 1}"
    pattern_2 = f"{int(num) - 1}{num}{int(num) + 1}"
    target = "".join(sorted(merged_suites[suite]))
    if pattern_1 in target or pattern_2 in target:
        return True
    return False


def bian_du(merged_suites, history):
    # 12(3)，1233(3)，(7)89，(7)7789计
    # 12345(3)，56789(7) 不计
    # 只听一张牌，等待这张牌的胡牌形式只有一种
    action = history[f"{len(history) - 1}"]["action"]
    play_action = history[f"{len(history) - 1}"]["play_action"]
    hu_tile = history[f"{len(history) - 1}"]["tile"]
    if action != "hu-add" and play_action != "shang":
        return False
    if len(hu_tile) == 1:
        return False
    num, suite = hu_tile[0], hu_tile[1]
    joined = "".join(sorted(merged_suites[suite]))
    print(joined)
    if "5" in joined:
        return False
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


def que_yi_men(merged_suites: dict):
    # has only two suits
    return len(merged_suites) == 2


def yao_jiu_ke(distinct_tiles) -> int:
    # 111, 999, 1111, 9999 and FENGS
    # for each count 1
    total_yao_jiu_ke = 0
    for k, v in distinct_tiles.items():
        if v == 3 and k in ("1万", "9万", "1筒", "9筒", "1索", "9索") + FENGS:
            total_yao_jiu_ke += 1
    return total_yao_jiu_ke


def lao_shao_fu(merged_suites: dict) -> int:
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


def lian_liu(merged_suites: dict) -> int:
    # 一种花色的连续六张牌 可以有多个
    total_lian_liu = 0
    for tiles in merged_suites.values():
        if len(tiles) >= 6:
            bptr = 0
            while bptr <= len(tiles) - 6:
                if int(tiles[bptr][0]) + 5 == int(tiles[bptr + 5][0]):
                    total_lian_liu += 1
                bptr += 5
    return total_lian_liu


# -------- 2番 --------


def duan_yao(tiles):
    # no 1, 9， FENGS, JIANS
    # cal_wu_zi = False
    for tile in tiles:
        if tile[0] in ("1", "9") + FENGS + JIANS:
            return False
    return True


def si_gui_yi(distinct_tiles: dict, gang_history, an_gang_history) -> int:
    # 4x same tile without gang for each count 1
    if gang_history or an_gang_history:
        return False
    ctr = 0
    for v in distinct_tiles.values():
        if v == 4:
            ctr += 1
    return ctr


def ping_hu(
    tiles,
    peng_history,
    gang_history,
    shang_history,
    an_gang_history,
    merged_suites: dict,
    jiangs,
):
    # 四副顺子及序数牌。边，坎，单调将不影响。不计无字牌
    for tile in tiles:
        if tile in FENGS + JIANS:
            return False
    if peng_history or gang_history or an_gang_history:
        return False
    shun_count = len(shang_history) // 3
    # alt to use get_shang_sets
    for suite, vals in merged_suites.items():
        vals = sorted(vals)
        while vals:
            min_val = vals.pop(0)
            if f"{min_val}{suite}" == jiangs:
                continue
            elif str(int(min_val) + 1) in vals and str(int(min_val) + 2) in vals:
                vals.remove(str(int(min_val) + 1))
                vals.remove(str(int(min_val) + 2))
                shun_count += 1
            else:
                break
    return shun_count == 4


def men_qian_qing(history: dict):
    # 没吃，碰，明杠。和他家出的牌
    for entry in history.values():
        if entry["play_action"] in ["shang", "peng", "ming_gang", "jia_gang"]:
            return False
    return True


def men_feng_ke(distinct_tiles: dict, player_wind):
    # 与自家本局相同的风刻
    # cal_yao_jiu_ke = False for this tile
    if player_wind in distinct_tiles and distinct_tiles[player_wind] >= 3:
        return True
    return False


def quan_feng_ke(distinct_tiles: dict, round_wind):
    # 与圈风相同的风刻
    # cal_yao_jiu_ke = False for this tile
    if round_wind in distinct_tiles and distinct_tiles[round_wind] >= 3:
        return True
    return False


# -------- 4番 --------


def bu_qiu_ren(history, gang_history, peng_history, shang_history):
    """没碰，明杠，吃，自摸和牌"""
    if gang_history or peng_history or shang_history:
        return False
    if history[str(len(history) - 1)]["action"] == "hu-add":
        return False
    return True


def quan_dai_yao(
    distinct_tiles: dict,
    peng_history,
    gang_history,
    an_gang_history,
    shang_history,
    jiangs,
):
    # 每副顺子、刻子、将牌都有幺九牌
    formatted_shang = {"索": [], "筒": [], "万": []}
    for i in range(0, len(shang_history) - 2, 3):
        suite = shang_history[i][1]
        comb = shang_history[i][0] + shang_history[i + 1][0] + shang_history[i + 2][0]
        formatted_shang[suite].append(comb)
    an_ke = []
    remaining_tiles = []
    for tile, cnt in distinct_tiles.items():
        if cnt >= 3:
            if tile == jiangs:
                remaining_tiles += [tile] * cnt
            else:
                an_ke += [tile]
        if cnt <= 2:
            remaining_tiles += [tile] * cnt
    total_yao_jiu_pai = 0
    for tile in set(peng_history + gang_history + an_gang_history):
        if len(tile) == 1 or tile[0] in ("1", "9"):
            total_yao_jiu_pai += 1
    for tile in set(an_ke):
        if len(tile) == 1 or tile[0] in ("1", "9"):
            total_yao_jiu_pai += 1
    for tile_groups in formatted_shang.values():
        for tile_group in tile_groups:
            if "1" in tile_group or "9" in tile_group:
                total_yao_jiu_pai += 1
    for tile in remaining_tiles:
        if len(tile) == 1 or tile[0] in ("1", "9"):
            total_yao_jiu_pai += 1
    return total_yao_jiu_pai == 6


# -------- 6番 --------


def quan_qiu_ren(tiles: list, an_gang_history, history):
    # 吃，碰，明杠x4，和他家的牌
    if an_gang_history:
        return False
    if len(tiles) != 2 or tiles[0] != tiles[1]:
        return False
    if history[str(len(history) - 1)]["action"] == "hu-add":
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


def hun_yi_se(merged_suites: dict, tiles):
    # 混一色，由一种花色序数牌及字牌组成的和牌
    # TODO merge with qing_yi_se?
    if len(merged_suites) != 1:
        return False
    suite = list(merged_suites.keys())[0]
    l = len(tiles) - len(merged_suites[suite])
    if l == 0:
        return False
    return True


def peng_peng_hu(distinct_tiles: dict):
    # 由四副刻子（或杠）组成的和牌
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


def san_se_san_jie_gao(merged_suites: dict):
    # 三色三节高 三种花色依次递增1的三副刻子
    if len(merged_suites) != 3:
        return False
    candits = {}
    for suite, tiles in merged_suites.items():
        bptr = 0
        fptr = 2
        while fptr < len(tiles):
            tmp = tiles[bptr : fptr + 1]
            if tmp[0] == tmp[1] and tmp[0] == tmp[2]:
                if suite not in candits:
                    candits[suite] = [tmp[0]]
                else:
                    if tmp[0] not in candits[suite]:
                        candits[suite].append(tmp[0])
                bptr += 3
                fptr += 3
            else:
                bptr += 1
                fptr += 1
    if len(candits) != 3:
        return False
    vals = []
    for candit in candits.values():
        vals += candit
    vals = "".join(sorted(vals))
    for i in range(0, len(vals) - 1):
        if i + 2 > len(vals) - 1:
            break
        if int(vals[i]) + 1 == int(vals[i + 1]) and int(vals[i + 1]) + 1 == int(
            vals[i + 2]
        ):
            return True
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


# -------- 12番 --------


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


def quan_dai_wu(
    tiles,
    distinct_tiles,
    peng_history,
    gang_history,
    an_gang_history,
    shang_history,
    jiangs,
):
    # 每副顺子、刻子、将牌都有序数牌5
    # can be improved i.e. jiang is not 5 immediate exit
    for tile in set(peng_history + gang_history + an_gang_history):
        if len(tile) == 1:
            return False
    an_ke = []
    remaining_tiles = []
    for tile, cnt in distinct_tiles.items():
        if cnt >= 3:
            if tile == jiangs:
                remaining_tiles += [tile] * cnt
            else:
                an_ke += [tile]
        if cnt <= 2:
            remaining_tiles += [tile] * cnt

    total_dai_wu_pai = 0

    for tile in set(an_ke):
        if len(tile) == 1 or tile[0] != "5":
            return False
        elif tile[0] == "5":
            total_dai_wu_pai += 1
    formatted_shang = {"索": [], "筒": [], "万": []}
    for i in range(0, len(shang_history) - 2, 3):
        suite = shang_history[i][1]
        comb = shang_history[i][0] + shang_history[i + 1][0] + shang_history[i + 2][0]
        formatted_shang[suite].append(comb)
    for tile_groups in formatted_shang.values():
        for tile_group in tile_groups:
            if "5" in tile_group:
                total_dai_wu_pai += 1
    for tile in remaining_tiles:
        if tile[0] == "5":
            total_dai_wu_pai += 1
    return total_dai_wu_pai == 6


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


def yi_se_san_jie_gao(merged_suites: dict):
    # 一色三节高，一种花色三副依次递增1的刻子
    # cal_yi_se_san_tong_shun = False
    for suite, tiles in merged_suites.items():
        tiles = sorted(tiles)
        if len(tiles) >= 9:
            bptr = 0
            fptr = 8
            while fptr < len(tiles):
                tmp = tiles[bptr : fptr + 1]
                if (
                    (tmp[0] == tmp[1] and tmp[0] == tmp[2])
                    and (
                        tmp[3] == tmp[4]
                        and tmp[3] == tmp[5]
                        and int(tmp[3]) - 1 == int(tmp[0])
                    )
                    and (
                        tmp[6] == tmp[7]
                        and tmp[6] == tmp[8]
                        and int(tmp[6]) - 1 == int(tmp[3])
                    )
                ):
                    return True
                else:
                    bptr += 1
                    fptr += 1
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


# -------- 32番 --------


def hun_yao_jiu(tiles):
    # 混幺九，由字牌和序数牌1、9组成的和牌
    for tile in tiles:
        if len(tile) == 1:
            continue
        if tile[0] not in ("1", "9"):
            return False
    return True


# -------- 48番 --------


def yi_se_si_jie_gao(merged_suites):
    # 一色四节高，一种花色四副依次递增1的刻子
    # cal_yi_se_san_tong_shun = False
    # cal_yi_se_san_jie_gao = False
    # cal_peng_peng_hu = False
    if len(merged_suites) != 1:
        return False
    distinct = {}
    suite = list(merged_suites.keys())[0]
    vals = merged_suites[suite]
    for tile in vals:
        if tile not in distinct:
            distinct[tile] = 1
        else:
            distinct[tile] += 1
    keys = [k for k, v in distinct.items() if v >= 3]
    if len(keys) != 4:
        return False
    if (
        int(keys[0]) + 1 == int(keys[1])
        and int(keys[1]) + 1 == int(keys[2])
        and int(keys[2]) + 1 == int(keys[3])
    ):
        return True
    return False


# -------- 64番 --------


def yi_se_shuang_long_hui(merged_suites: dict):
    # 一色双龙会，一种花色两副老少副和本花色5的将牌
    # cal_qi_dui = False
    # cal_qing_yi_se = False
    # cal_ping_hu = False
    # cal_lao_shao_fu = False
    # cal_yi_ban_gao = False
    # cal_wu_zi = False
    # based on `lao_shao_fu`, if rv == 2 then check yi_se_shuang_long_hui
    if len(merged_suites) != 1:
        return False
    suite = list(merged_suites.keys())[0]
    if "".join(sorted(merged_suites[suite])) != "11223355778899":
        return False
    return True


def zi_yi_se(tiles):
    # 字一色，全部由字牌组成的和牌
    for tile in tiles:
        if tile not in JIANS + FENGS:
            return False
    return True


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


def jiu_lian_bao_deng(merged_suites: dict, tiles):
    # 九莲宝灯，一种花色序数牌1112345678999+本花色任何牌成和牌
    if len(merged_suites) != 1:
        return False
    suite = list(merged_suites.keys())[0]
    if len(merged_suites[suite]) != len(tiles):
        return False
    nums = sorted(merged_suites[suite])
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
