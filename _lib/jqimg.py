#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二十四节气排版模板 · 共用取图工具

三套模板（节气卷 / 留白笺 / 六色四季）都从这里取图，避免同一套裁切逻辑抄三遍。

六张插画的金线（#C9A227 山脊线）高度各不相同——金线顶从 y=330 到 y=572 都有。
所以裁切一律以「该张图自己的金线位置」为锚点，写死 y 区间会让某些图只剩半座山。

用法：
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_lib"))
    from jqimg import SERIES, load, gold_top, band, fade_top, fade_edges, accent, save
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.abspath(os.path.join(HERE, "..", "素材"))

# 顺序 = 时间顺序（立春 → 大雪）
# (文件, 节气名, 拼音, 三候注, 诗句, 公历)
SERIES = [
    ("01-lichun.png",      "立春", "LICHUN · BEGINNING OF SPRING", "一候 东风解冻", "春到人间草木知", "2月4日前后"),
    ("02-qingming.png",    "清明", "QINGMING · PURE BRIGHTNESS",  "三候 虹始见",   "沾衣欲湿杏花雨", "4月5日前后"),
    ("03-xiazhi.png",      "夏至", "XIAZHI · SUMMER SOLSTICE",   "三候 半夏生",   "映日荷花别样红", "6月21日前后"),
    ("04-bailu.png",       "白露", "BAILU · WHITE DEW",          "三候 群鸟养羞", "秋水共长天一色", "9月8日前后"),
    ("05-shuangjiang.png", "霜降", "SHUANGJIANG · FROST DESCENT", "三候 蛰虫咸俯", "霜叶红于二月花", "10月23日前后"),
    ("06-daxue.png",       "大雪", "DAXUE · MAJOR SNOW",         "三候 荔挺出",   "一树寒梅白玉条", "12月7日前后"),
]

# 系列四季色板（取自总览图右下角的规范）
PALETTE = {
    "嫩绿": "#A8C66C",
    "烟青": "#7E9E9A",
    "碧荷": "#3F8E7E",
    "月白": "#CDE3E6",
    "丹红": "#C0563E",
    "雪白": "#F2F4F5",
}

PAPER = (250, 246, 236)     # #FAF6EC 宣纸暖白（六张已统一校到这个值）
GOLD = (201, 162, 39)       # #C9A227 金线


def load(fname):
    return Image.open(os.path.join(ASSETS, fname)).convert("RGB")


def gold_top(im, step=3, need=2):
    """找出金线最高的那条 y —— 只用作兜底，不要直接当裁切锚点。

    注意：这只是「第一处出现金色」的位置，可能撞上金色的叶子（霜降的柿子叶就是
    金黄色的），或者一枚杂点（大雪的 gold_top 是 367，真山脊在 588）。
    裁切锚点一律用下面的 gold_axis()。
    """
    w, h = im.size
    px = im.load()
    for y in range(0, h):
        cnt = 0
        for x in range(0, w, step):
            r, g, b = px[x, y]
            if r > 175 and g > 130 and b < 125:
                cnt += 1
        if cnt > need:
            return y
    return int(h * 0.45)      # 兜底


def band(im, top, height):
    """裁一条高 height 的横带，top 越界时整体平移回来。"""
    w, h = im.size
    if top + height > h:
        top = h - height
    top = max(0, top)
    return im.crop((0, top, w, top + height))


def gold_axis(im, step=3):
    """金线主体所在的 y —— 裁「窄带」用这个锚点。

    做法：逐行数金色像素，取数量最多的那一行。
    山脊线是横贯画面的长线，落在某一行的金色像素数会明显多于零散的金色叶子，
    所以 argmax 比「第一处出现金色」稳得多。

    两个真实踩过的坑：
      · 霜降的柿子叶是金黄色，gold_top 会被叶子骗到 y=360，而真正的山脊在 478，
        按 360 裁出来的带里只有天空。
      · 大雪的 gold_top=367 是杂点，真山脊在 588。
    """
    w, h = im.size
    px = im.load()
    best_y, best_c = int(h * 0.45), -1
    for y in range(0, h):
        cnt = 0
        for x in range(0, w, step):
            r, g, b = px[x, y]
            if r > 175 and g > 130 and b < 125:
                cnt += 1
        if cnt > best_c:
            best_y, best_c = y, cnt
    return best_y


def band_anchor(im, up, height):
    """以「金线主体」为锚点，向上留 up 像素，再裁固定高度。"""
    return band(im, gold_axis(im) - up, height)


def fade_top(im, px=90):
    """顶部 alpha 由 0 渐到 255。

    裁切会把垂下的柳枝 / 飞鸟 / 云气从中间切断，留一条硬边。
    顶边渐隐 + 背景同色，接缝就化没了。
    """
    im = im.convert("RGBA")
    w, h = im.size
    mask = Image.new("L", (1, h), 255)
    mp = mask.load()
    for y in range(px):
        mp[0, y] = int(255 * y / px)
    im.putalpha(mask.resize((w, h), Image.BILINEAR))
    return im


def fade_edges(im, left=110, right=110):
    """左右两端横向渐隐，让横带像一条飘在山间的云带，而不是一张切过边的图。"""
    im = im.convert("RGBA")
    w, h = im.size
    mask = Image.new("L", (w, 1), 255)
    mp = mask.load()
    for x in range(left):
        mp[x, 0] = int(255 * x / left)
    for x in range(right):
        mp[w - 1 - x, 0] = int(255 * x / right)
    im.putalpha(mask.resize((w, h), Image.BILINEAR))
    return im


def accent(im, drop_gold=True):
    """抽这张图的主色（插画里的青绿、丹红那一类），返回十六进制。

    做法：按色相分 12 个桶，只统计有饱和度、不太亮也不太暗的像素，
    丢掉金色区间（金线会污染结果），取最大的那个桶的均值。
    """
    import colorsys
    from collections import defaultdict

    small = im.resize((160, max(1, round(im.height * 160 / im.width))), Image.LANCZOS)
    bins = defaultdict(list)
    for r, g, b in small.getdata():
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s < 0.16 or v < 0.24 or v > 0.9:
            continue
        deg = h * 360
        if drop_gold and 33 <= deg <= 58:
            continue
        bins[int(deg // 30)].append((r, g, b))
    if not bins:
        return "#8A8378"
    key = max(bins, key=lambda k: len(bins[k]))
    px = bins[key]
    n = len(px)
    r, g, b = (sum(p[i] for p in px) // n for i in range(3))
    return "#%02X%02X%02X" % (r, g, b)


def tone(hexcolor, factor=0.78):
    """把颜色调暗一点，好当正文/标题色用（月白那一类太浅，印在白底上看不见）。"""
    hexcolor = hexcolor.lstrip("#")
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(c * factor))) for c in (r, g, b))


def round_corners(im, radius=24, bg=(255, 255, 255)):
    """把四角切成圆角，圆角外侧填成底纸色。

    为什么要把圆角「烧」进 PNG 而不是靠 CSS border-radius：
    粘进公众号之后 style 能不能活下来由编辑器决定，烧进像素就一定能活。
    插画本身是暖白 #FAF6EC，底纸也是白，所以填色看不出接缝。
    """
    im = im.convert("RGB")
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    out = Image.new("RGB", (w, h), bg)
    out.paste(im, (0, 0), mask)
    return out


def save(im, path):
    im.save(path, "PNG", optimize=True)
    print("  %-30s %sx%s  %6.0f KB" % (
        os.path.basename(path), im.size[0], im.size[1], os.path.getsize(path) / 1024))
