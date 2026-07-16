#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從遊戲設定檔自動更新 README.md 的派系卡牌介紹。

資料來源(以遊戲內顯示為準):
  FOS brainstorming/config/card_hints.json   — 卡牌提示文字(第一行為攻擊方式, 其餘為效果敘述)
  FOS brainstorming/config/card_setting.json — 血量 / 攻擊 / 進化費用等數值

README.md 中每個派系的卡牌列表都被一對標記包住:
  <!-- AUTO-CARDS:White START --> ... <!-- AUTO-CARDS:White END -->
本腳本只改寫標記之間的內容, 標記外的手寫說明不會被動到。

用法:
  python tools/update_readme.py          # 直接改寫 README.md
  python tools/update_readme.py --check  # 只檢查是否過期(過期回傳非零, 適合 CI / pre-commit)
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HINTS_PATH = ROOT / "FOS brainstorming" / "config" / "card_hints.json"
SETTING_PATH = ROOT / "FOS brainstorming" / "config" / "card_setting.json"
README_PATH = ROOT / "README.md"

# (card_setting.json 的 key, card_hints.json 的字尾, 對應 cards/card_*.py 的 color_code)
FACTIONS = [
    ("White", "W"),
    ("Red", "R"),
    ("Green", "G"),
    ("Blue", "B"),
    ("Orange", "O"),
    ("DarkGreen", "DKG"),
    ("Cyan", "C"),
    ("Fuchsia", "F"),
    ("Brown", "BR"),
    ("Purple", "P"),
]

JOBS = [
    ("ADC", "三角形"),
    ("AP", "圓形"),
    ("TANK", "方形"),
    ("HF", "梯形"),
    ("LF", "雙菱形"),
    ("ASS", "刺客"),
    ("APT", "六邊形"),
    ("SP", "鑽石"),
]

# 顯示數值的特例(綠色鑽石的血攻是官方玩笑, 不直接寫出)
STAT_OVERRIDES = {("Green", "SP"): "?/?"}

# 提示文字的換行只是遊戲內排版, 接合時視斷點前後判斷要不要補「，」:
# 斷在虛詞/連接詞後、數字或符號前、或動詞與受詞之間時直接接起來, 其餘補「，」。
_NO_SEP_AFTER_CHARS = "(（)）/，。、：:,%"
_NO_SEP_AFTER_WORDS = ("的", "之", "且", "並", "則", "對", "將", "使",
                       "由", "及", "或", "而", "內", "造成", "計算", "隨機")
_NO_SEP_BEFORE_CHARS = "/()（），。、：:,+-0123456789"
_NO_SEP_BEFORE_WORDS = ("的", "及", "附加", "開始", "失去")


def _needs_separator(prev: str, nxt: str) -> bool:
    if prev[-1] in _NO_SEP_AFTER_CHARS or prev.endswith(_NO_SEP_AFTER_WORDS):
        return False
    if nxt[0] in _NO_SEP_BEFORE_CHARS or nxt.startswith(_NO_SEP_BEFORE_WORDS):
        return False
    if nxt.startswith("造成") and not prev[-1].isdigit():
        return False
    return True


def _join_hint_lines(lines: list[str]) -> str:
    out = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if out and _needs_separator(out, line):
            out += "，"
        out += line
    return out


def _format_stats(faction: str, job: str, setting: dict) -> str:
    override = STAT_OVERRIDES.get((faction, job))
    if override:
        return override
    stats = setting.get(faction, {}).get(job)
    if not stats:
        return "?/?"
    text = f"{stats['health']}/{stats['damage']}"
    if "cost" in stats:  # 淺藍派系: 括弧內為進化費用
        text += f"({stats['cost']})"
    return text


def build_faction_block(faction: str, suffix: str, hints: dict, setting: dict) -> str:
    lines = []
    for job, zh_name in JOBS:
        hint = hints.get(job + suffix, "").strip()
        if not hint:  # 尚未實裝的卡(如紫色部分職業)
            continue
        parts = hint.split("\n")
        pattern = parts[0].strip()
        desc = _join_hint_lines(parts[1:])
        # 淺藍進化數值 (+1+2) -> (+1/+2), 跟舊版 README 的寫法一致
        desc = re.sub(r"\(\+(\d+)\+(\d+)\)", r"(+\1/+\2)", desc)
        line = f"- **{zh_name}({job})-{_format_stats(faction, job, setting)}-{pattern}**"
        if desc:
            if not desc.endswith("。"):
                desc += "。"
            line += f"/{desc}"
        lines.append(line)
    return "\n".join(lines)


def render_readme(text: str, hints: dict, setting: dict) -> str:
    for faction, suffix in FACTIONS:
        start = f"<!-- AUTO-CARDS:{faction} START -->"
        end = f"<!-- AUTO-CARDS:{faction} END -->"
        if start not in text or end not in text:
            sys.exit(f"README.md 缺少 {faction} 的標記 {start} / {end}")
        block = build_faction_block(faction, suffix, hints, setting)
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        text = pattern.sub(f"{start}\n{block}\n{end}", text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="只檢查 README 是否為最新, 過期則以非零狀態碼結束")
    args = parser.parse_args()

    hints = json.loads(HINTS_PATH.read_text(encoding="utf-8"))
    setting = json.loads(SETTING_PATH.read_text(encoding="utf-8"))
    old = README_PATH.read_text(encoding="utf-8")
    new = render_readme(old, hints, setting)

    if new == old:
        print("README.md 已是最新")
        return
    if args.check:
        sys.exit("README.md 已過期, 請執行: python tools/update_readme.py")
    README_PATH.write_text(new, encoding="utf-8")
    print("README.md 已更新")


if __name__ == "__main__":
    main()
