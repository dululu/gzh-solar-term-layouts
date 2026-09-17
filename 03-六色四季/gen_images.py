#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套三「六色四季」· 取图

和另两套最大的不同：这里的插画不是「铺满整幅的背景」，而是**圆角图卡**。
四角在 PNG 里就切成圆角、外侧填白，粘进公众号不依赖 CSS border-radius
（样式被编辑器剥掉时，圆角也不会跟着消失）。

产出：
  卡带-*.png     1400×645 圆角图卡，正文里的章节分隔
  头卡-霜降.png  1560 宽大图卡，头图右下用
  尾卡-大雪.png  1174 宽图卡，结尾图用
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "_lib")))

from jqimg import SERIES, band, fade_top, gold_axis, load, round_corners, save  # noqa: E402

OUT = os.path.join(HERE, "图")

CARD_TOP = 200        # 图卡比段带多留一点天空，因为卡片自带边框感，天空多一点更透气
CARD_H = 580


def card(im, top=CARD_TOP, height=CARD_H, width=None, radius=26, fade=0):
    b = band(im, top, height)
    if width:
        b = b.resize((width, round(b.height * width / b.width)), Image.LANCZOS)
    if fade:
        # 头图/结尾图的卡片上沿会切到垂下来的枝叶，先渐隐再切圆角就不留硬边
        b = fade_top(b, fade)
    return round_corners(b, radius, (255, 255, 255))


def main():
    os.makedirs(OUT, exist_ok=True)
    print("套三「六色四季」取图 →", OUT)

    for fname, cn, *_ in SERIES:
        im = load(fname)
        # 正文图卡：统一 y 区间，和其它两套同一套版式网格
        save(card(im, CARD_TOP, CARD_H, width=1400, radius=24),
             os.path.join(OUT, "卡带-%s.png" % cn))

    # 头图大卡：取霜降，金线落在卡片偏下处，上方留白压字。
    # 高度卡在 240px（换算到 1560 宽约 297px）——再高就会把标题挤掉。
    sj = load("05-shuangjiang.png")
    save(card(sj, gold_axis(sj) - 130, 240, width=1560, radius=26, fade=110),
         os.path.join(OUT, "头卡-霜降.png"))
    # 结尾卡
    dx = load("06-daxue.png")
    save(card(dx, gold_axis(dx) - 170, 260, width=1174, radius=22, fade=110),
         os.path.join(OUT, "尾卡-大雪.png"))


if __name__ == "__main__":
    main()
