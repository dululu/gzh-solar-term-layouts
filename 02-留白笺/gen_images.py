#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套二「留白笺」· 取图

和套一最大的不同：不要「整幅画当分隔」，只要**一条窄带**。
窄带只保留山脊线那一段（金线上下各留一点），左右两端做渐隐，
在近白底上看起来就像一条飘着的云带，而不是一张切过边的图片。

产出：
  窄带-*.png    1400×170，正文里的章节分隔（显示 677×82，很轻）
  头带-*.png    1800×300，头图压标题用
  尾带-大雪.png 1354×260，结尾图用
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "_lib")))

from jqimg import SERIES, band, fade_edges, fade_top, gold_axis, load, save  # noqa: E402

OUT = os.path.join(HERE, "图")


def ridge(im, up, down, width=None, edge=0, top_fade=0):
    """以金线为轴取一条横带（上 up、下 down），可缩放、可渐隐。"""
    a = gold_axis(im)
    b = band(im, a - up, up + down)
    if width:
        b = b.resize((width, round(b.height * width / b.width)), Image.LANCZOS)
    if edge:
        b = fade_edges(b, edge, edge)
    if top_fade:
        b = fade_top(b, top_fade)
    return b


def main():
    os.makedirs(OUT, exist_ok=True)
    print("套二「留白笺」取图 →", OUT)

    for fname, cn, *_ in SERIES:
        im = load(fname)
        # 正文窄带：只留山脊 + 一点点山体，左右渐隐
        save(ridge(im, 72, 98, width=1400, edge=170), os.path.join(OUT, "窄带-%s.png" % cn))

    # 头图带：取霜降（红叶，颜色最活）的宽景。
    # 注意 up 必须大于 fade —— 否则渐隐会把金线本身也吃掉，带上就只剩纸。
    save(ridge(load("05-shuangjiang.png"), 150, 120, width=1800, top_fade=120),
         os.path.join(OUT, "头带-霜降.png"))
    # 结尾带：大雪，天上多留一点压字
    save(ridge(load("06-daxue.png"), 170, 110, width=1354, top_fade=130),
         os.path.join(OUT, "尾带-大雪.png"))


if __name__ == "__main__":
    main()
