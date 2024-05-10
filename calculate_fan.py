FENGS = ("东", "南", "西", "北")
JIANS = ("中", "发", "白")
HUAS = ("春", "夏", "秋", "冬", "梅", "蘭", "菊", "竹")


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


# -------- 1番 --------


def _hua_pai(tiles):
    # 每花1番。花牌补花成和计自摸，不计杠上开花
    pass


def zi_mo(history):
    # TODO might be a convinient fn to have
    return history[-1][0] == "HU"


def dan_qi_dui_zi(tiles):
    # if drawed tile forms eye to hu
    # 只听一张牌，等待这张牌的胡牌形式只有一种
    pass


def kan_zhang(tiles):
    # if drawed tile is in between two tiles and leads to hu
    # 4556, 5 is kan zhang
    # 45567, 6 is not
    # 只听一张牌，等待这张牌的胡牌形式只有一种
    pass


def bian_du(tiles):
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
    pass


def que_yi_men(tiles):
    # has only two suits
    pass


def yao_jiu_ke(tiles):
    # 111, 999, 1111, 9999 and FENGS
    # for each count 1
    pass


def lao_shao_fu(tiles):
    # 123 and 789 of a single suite
    # for each count 1
    pass


def lian_liu(tiles):
    # 一种花色的连续六张牌
    # for each count 1
    pass


def xi_xiang_feng(tiles):
    # 2 suites of same shang i.e. 123
    # for each count 1
    pass


def yi_ban_gao(tiles):
    # one suite 2x of shang
    # for each count 1
    pass


# -------- 2番 --------


def duan_yao(tiles):
    # no 1, 9， FENGS, JIANS
    # cal_wu_zi = False
    pass


def an_gang(history):
    pass


def shuang_an_ke(tiles):
    # 2x an ke or an gang
    pass


def shuang_tong_ke(tiles):
    # 2 suite of same ke
    # for each count 1
    pass


def si_gui_yi(tiles):
    # 4x same tile without gang
    # for each count 1
    pass


def ping_hu(tiles):
    # 四副顺子及序数牌。边，坎，单调将。不计无字牌
    # cal_wu_zi = False
    pass


def men_qian_qing(history):
    # 没吃，碰，杠。和他家出的牌
    # cal_zi_mo = False
    pass


def men_feng_ke(tiles):
    # 与自家本局相同的风刻
    # cal_yao_jiu_ke = False for this tile
    pass


def quan_feng_ke(tiles):
    # 与圈风相同的风刻
    # cal_yao_jie_ke = False for this tile
    pass


# -------- 2番 --------


def he_jue_zhang(tiles):
    # 和牌池、桌面已亮明的第四张牌
    # 抢杠和不计和绝张
    pass


def calculate_fan(
    tiles, shang_history, peng_history, gang_history, history, round_wind, player_wind
):
    """ """
    total_fan = 0

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
