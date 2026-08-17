# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / Five O'clock Shadow Studio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------

"""Chinese names for tower content.

Kept apart from ``content.py`` so the mechanics and the wording can move
independently - an entry missing here just falls back to English.
Most of these are the names from the original design notes; the English in
``content.py`` was derived from them in the first place.

Each entry is ``(name, description)``.
"""

from __future__ import annotations

from tower.content import JOBS

ROOMS_ZH: dict[str, str] = {
    "event": "事件", "shop": "商店", "gold_mine": "金礦", "relic_chest": "遺物寶箱",
}

BLESSINGS_ZH: dict[str, tuple[str, str]] = {
    "two_cards": ("招兵買馬", "依序進行 2 次選牌加入"),
    "enchant_unit": ("祝福之鋼", "為 1 個棋子進行附魔（鋒利或加固）"),
    "one_relic": ("幸運拾獲", "獲得 1 個隨機遺物"),
    "gold_150": ("滿載錢袋", "獲得 150 金幣"),
    "bench_plus": ("擴建營地", "備戰區格子數 +2"),
    "one_orb": ("澄澈心智", "獲得 1 個遺忘寶珠"),
    "orbs_and_curse": ("惡魔的交易", "獲得 3 個遺忘寶珠，然後選擇 1 個詛咒遺物"),
    "power_and_curse": ("受詛咒的力量", "從 3 個強力遺物中選 1 個，並獲得 1 個隨機詛咒遺物"),
    "relics_and_curse": ("盜墓", "獲得 2 個遺物和 1 個隨機詛咒遺物"),
    "gold_and_curse": ("血腥錢財", "獲得 300 金幣和 1 個隨機詛咒遺物"),
}

# free-standing lines the event screens print
EVENT_TEXT_ZH: dict[str, str] = {
    # shared
    "leave": "離開",
    "take_it_or_leave_it": "拿或不拿",
    "take_none": "都不拿",
    "leave_them": "全部放棄",
    "leave_it": "不拿",
    # altar
    "altar_title": "{faction}祭壇",
    "altar_subtitle": "你靠近時，石頭發出低鳴",
    "altar_accepted": "獻祭完成",
    "deal_orb": ("獻祭", "獻上 150 金幣獲得遺忘寶珠"),
    "deal_relic": ("貢品", "獻上 150 金幣獲得一個遺物"),
    "deal_unit": ("徵召", "獻上 50 金幣獲得一個隨機棋子"),
    "deal_spell": ("咒文", "獻上 50 金幣獲得一個隨機法術"),
    "deal_card_choice": ("祈願", "獻上 100 金幣選擇一張牌"),
    "deal_gold_100": ("祝福", "祭壇賜予你 100 金幣"),
    "deal_gold_150": ("大祝福", "祭壇賜予你 150 金幣"),
    # relic trader
    "trader_title": "遺物交換商",
    "trader_subtitle": "你的一件換我的一件",
    # tinker
    "tinker_title": "維修工匠",
    "tinker_strip": ("拆除", "移除一張牌的附魔"),
    "tinker_reforge": ("加工", "將一張牌的附魔轉化為{grade}"),
    "tinker_strip_prompt": "要拆除哪一張的附魔？",
    "tinker_reforge_prompt": "要把哪一張加工成{grade}？",
    # visitor
    "visitor_title": "{faction}訪客",
    "visitor_subtitle": "他打開了一箱貨物",
    "visitor_unit": ("購買棋子", "從三個{faction}棋子中選一個"),
    "visitor_relic": ("購買遺物", "一個{faction}遺物"),
    "visitor_fight": ("來一把吧！", "打贏他，兩樣都免費"),
    "visitor_leave": ("就此告辭", "免費獲得一個隨機{faction}棋子"),
    "visitor_choose_unit": "選擇一個棋子",
    # act 3
    "statue_title": "凶暴野獸雕像",
    "statue_subtitle": "它的下顎被無數雙手摸得發亮",
    "statue_touch": ("觸摸雕像", "為一個棋子附魔狂化"),
    "statue_prompt": "要讓哪一個棋子狂化？",
    "prism_title": "三稜鏡",
    "prism_subtitle": "它把火光拆成各個派系的顏色",
    "prism_light": ("將牌舉向光源", "為一張牌附魔色散"),
    "prism_shard": ("收下碎片", "獲得 {gold} 金幣"),
    "prism_prompt": "要讓哪一張白色牌色散？",
    # wanderer
    "wanderer_title": "流浪商人",
    "wanderer_text": "他用 {gold} 金幣收走了你多餘的裝備",
    # rooms
    "mine_title": "金礦",
    "mine_text": "你挖出了 {gold} 金幣",
    "chest_title": "遺物寶箱",
    "empty_title": "空房間",
    "empty_text": "這裡什麼都沒有",
    # blessings
    "blessing_title": "起手祝福",
    "blessing_subtitle": "三個之中選一個",
}

TIERS_ZH: dict[str, str] = {
    "common": "普通", "rare": "稀有", "power": "強力",
    "special": "特殊", "curse": "詛咒",
}

RELICS_ZH: dict[str, tuple[str, str]] = {
    # ---------------- 普通 ----------------
    "courier": ("送貨員", "免費刷新商店一次，並可額外刷新一次"),
    "first_aid_kit": ("急救包", "你的治療法術額外治療 2 點生命"),
    "dorans_shield": ("多蘭盾", "你放置的第一個棋子 +2 生命值"),
    "dorans_blade": ("多蘭劍", "你放置的第一個棋子 +1 攻擊力"),
    "seal_of_radiance": ("光輝之印", "拾起時為一張牌附魔光輝"),
    "piggy_bank": ("小豬撲滿", "獲得的金錢增加 25%"),
    "index_fund": ("指數型投資組合", "每層獲得 10% 當前金錢，直到你在商店消費"),
    "cuckoo_clock": ("咕咕鐘", "當你洗牌時，抽一張牌"),
    "pocket_watch": ("懷錶", "當你洗牌時，獲得一次攻擊次數"),
    "credit_card": ("信用卡", "商店可預支最多 200 金幣，還清前每層增加 10% 債務"),
    "blue_crystal_ball": ("藍色水晶球", "激發魔力球時，對隨機敵人造成 1 點傷害"),
    "ship_in_a_bottle": ("瓶中海盜船", "獲得勝利後，牌組中每個海盜讓你獲得 20 金幣"),
    "palanquin": ("人力轎子", "備戰區格子數 +2"),
    "rabbits_foot": ("兔子腳", "你的起始幸運 +15%"),
    "mob_pigeon": ("黑道信鴿", "在你第四回合時，獲得一張移動法術"),
    "giant_mushroom": ("巨人蘑菇", "拾起時為一張牌附魔巨人症"),
    "ninja_scroll": ("忍術卷軸", "單次攻擊打到同一個敵人兩次時，額外造成 2 點傷害"),

    # ---------------- 稀有 ----------------
    "prepared_pack": ("準備背包", "起始手牌 +1"),
    "coupon": ("折價券", "商店賣的商品打 5 折"),
    "ring_of_healing": ("治療之環", "你因溢補產生的護盾量加倍"),
    "dorans_ring": ("多蘭戒", "你使用的第一個法術使你抽一張牌"),
    "message_in_a_bottle": ("瓶中信", "每三回合，隨機給予你一張虛化的法術牌"),
    "blasting_wand": ("爆裂魔杖", "你的法師攻擊力 +2，法師不再麻痺敵人"),
    "blue_sigil": ("藍色印章", "拾起時為一張牌附魔魔力"),
    "mages_blood": ("法師之血", "回合開始時不再抽牌，改為獲得 3 顆魔力球"),
    "treasure_chest": ("藏寶箱", "你回合開始時獲得 2 枚硬幣"),
    "curse_ward": ("詛咒御守", "不會獲得詛咒遺物"),
    "strategists_fan": ("孔明神算", "當你場上的友方單位少於 1，額外獲得 1 分"),
    "burning_blood": ("燃燒之血", "拾起時為一張牌附魔活力"),
    "talaria": ("塔拉里亞", "拾起時為一張牌附魔飛行"),
    "razor_hat": ("剃刀帽", "當有單位移動後，對場上隨機敵人造成 1 點傷害"),
    "radiant_totem": ("光輝圖騰", "你每有 20 圖騰，額外獲得 1 分"),
    "carvers_licence": ("雕刻師執照", "拾起時為一張牌附魔雕刻師"),
    "hidden_dagger": ("隱匿匕首", "回合結束時，對站在影子上的敵方單位造成 1 點傷害"),
    "unchanging_stone": ("不變石", "拾起時為一張牌附魔堅定"),

    # ---------------- 強力 ----------------
    "sewing_kit": ("針線包", "當你造成的傷害小於 2 點，改為造成 2 點傷害"),
    "layered_armor": ("多層護甲", "拾起時為一張牌附魔覆甲"),
    "sword_boomerang": ("飛劍迴力鏢", "拾起時為一張牌附魔飛劍"),
    "wax_furnace": ("融蠟爐", "有附魔的棋子攻擊力 +1"),
    "oni_mask": ("赤鬼面具", "每當你的一個棋子成長 2 點攻擊力，他獲得 1 點護甲"),
    "carving_knife": ("雕刻刀", "回合開始時雕刻 1"),
    "echo_stone": ("迴響石", "拾起時為一張牌附魔迴響"),

    # ---------------- 特殊 ----------------
    "limit_break": ("上限突破", "你的牌組沒有上限，且可任意分配使用備戰區"),
    "demon_emblem": ("惡魔徽章", "牌組內超過 6 張法術時，所有棋子 +2 生命值、+1 攻擊力"),
    "mana_spring": ("魔力泉水", "回合開始時，獲得 1 顆魔力球"),
    "battle_focus": ("戰鬥專注", "每回合獲得 +1 攻擊次數，你的攻擊次數回合結束時歸 0"),
    "pacifism": ("和平主義", "你不會獲得攻擊次數，每回合開始時額外抽一張牌"),
    "tank_bloodline": ("坦克血脈", "若牌組中的棋子只有坦克，你的坦克 +3 生命值"),

    # ---------------- 詛咒 ----------------
    "worn_pack": ("破舊背包", "起始手牌 -1"),
    "torn_wallet": ("破損錢包", "每層失去 20 金幣"),
    "feeble_charm": ("無力護符", "你打出的第一張牌攻擊力 -2"),
    "hot_potato": ("燙手山芋", "隨機為牌組中的一張牌附魔灼傷"),
    "bloodied_needle": ("染血刺針", "選擇並為牌組中的一張牌附魔失血"),
    "rusted_statue": ("鏽蝕雕像", "隨機為牌組中的一張牌附魔鏽蝕"),
    "fog_of_war": ("戰爭迷霧", "看不到強化層的房間種類"),
    "sunglasses": ("墨鏡", "敵人變成未知"),
    "chipped_crown": ("缺角王冠", "每場戰鬥的起始分數 -1"),
}

# the eight job amulets and emblems follow one pattern each
for _job in JOBS:
    RELICS_ZH[f"amulet_{_job}"] = (f"{_job} 護符", f"你的 {_job} 職業牌的生命值 +1")
    RELICS_ZH[f"emblem_{_job}"] = (f"{_job} 徽章", f"你的 {_job} 職業牌的攻擊力 +1")


ENCHANTS_ZH: dict[str, tuple[str, str]] = {
    "disperse": ("色散", "入場時隨機變成其他派系的顏色，職業和體質不變"),
    "sharp": ("鋒利", "攻擊力 +1"),
    "fort": ("加固", "生命值 +2"),
    "rage": ("狂化", "攻擊力 +2、生命值 -2"),
    "mana": ("魔力", "打出時獲得 1 顆魔力球"),
    "radiant": ("光輝", "計分時額外 +1 分"),
    "steady": ("堅定", "免疫暈眩"),
    "plated": ("覆甲", "受到的傷害 -1"),
    "ghost": ("虛化", "回合結束會從手上消失，死亡時不會進入棄牌堆"),
    "chimera": ("合成獸", "這是一隻合成獸"),
    "borrowed": ("借用", "這張牌屬於別人，死亡時不會進入棄牌堆"),
    "sword": ("飛劍", "若攻擊範圍內沒有敵人，則攻擊最近的敵方"),
    "art_hero": ("工匠：英雄", "攻擊力 +1、生命值 +1"),
    "art_guard": ("工匠：守護", "生命值 +3"),
    "art_mend": ("工匠：癒合", "每回合開始時恢復 1 點生命值"),
    "vigor": ("活力", "回合結束時恢復 1 點生命"),
    "flight": ("飛行", "移動範圍擴展至全圖"),
    "carver": ("雕刻師", "攻擊造成傷害時 +1 圖騰"),
    "gigantism": ("巨人症", "體質加倍，但無法攻擊"),
    "echo": ("迴響", "攻擊次數大於 2 時，攻擊消耗兩次攻擊次數，傷害加倍"),
    "burn": ("灼傷", "第一次打出時，對手獲得 2 分"),
    "bleed": ("失血", "回合開始時，受到 1 點傷害"),
    "rust": ("鏽蝕", "無法獲得護盾"),
}
