#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套一「节气卷」· 取图

产出三类图：
  头带-*.png     1800 宽的「金线横带」，给头图压标题用
  段带-*.png     1260×580 的整幅横带，正文里做章节分隔（每章一张，按时间推进）
  尾带-大雪.png  1354 宽的横带，给结尾图用（时间线的终点 = 大雪）

裁切原则（踩过的坑都在这里）：
  · 底边一律切在**图片下沿**，这样底边永远不会出现半路截断的硬边
  · 段带用统一的 y 区间（260→840）：六张插画共用同一套版式网格，山脊都落在下半幅，
    统一切法反而让六章的节奏一致；顶边叠 120px alpha 渐隐化掉接缝
  · 头带/尾带要以金线为轴，锚点用 gold_axis（argmax），不能用 gold_top
    ——霜降的柿子叶是金黄色、大雪有杂点，按「第一处金色」裁会只剩天空
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "_lib")))

from jqimg import SERIES, band, fade_top, gold_axis, load, save  # noqa: E402

OUT = os.path.join(HERE, "图")

BAND_TOP = 260        # 段带统一从这个 y 开始裁
BAND_H = 580          # 1260 宽 → 2.17:1，正文里显示 677×312


def feature_band(im, above=150, below=120, width=None, fade=0):
    """以金线为轴取一条横带。above 必须大于 fade，否则渐隐会把金线本身也吃掉。"""
    b = band(im, gold_axis(im) - above, above + below)
    if width:
        b = b.resize((width, round(b.height * width / b.width)), Image.LANCZOS)
    if fade:
        b = fade_top(b, fade)
    return b


def main():
    os.makedirs(OUT, exist_ok=True)
    print("套一「节气卷」取图 →", OUT)

    for fname, cn, *_ in SERIES:
        im = load(fname)
        # 头图用的金线横带（1800 宽，顶部渐隐）
        save(feature_band(im, 150, 120, width=1800, fade=120),
             os.path.join(OUT, "头带-%s.png" % cn))
        # 正文段带：统一切 y=260→840，底边贴图片下沿
        save(fade_top(band(im, BAND_TOP, BAND_H), 120),
             os.path.join(OUT, "段带-%s.png" % cn))

    # 结尾带：时间线终点取大雪，天上多留一点好压字
    save(feature_band(load("06-daxue.png"), 170, 110, width=1354, fade=130),
         os.path.join(OUT, "尾带-大雪.png"))


if __name__ == "__main__":
    main()
