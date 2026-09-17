#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套一「节气卷」· 正文模板生成器

版式语言
  · 底：宣纸暖白 #FAF6EC，正文宋体，不用色块、不用边框
  · 时间：六张节气段带按 立春 → 清明 → 夏至 → 白露 → 霜降 → 大雪 顺序推进，
         每张段带就是一次「时间跳一格」
  · 章头：节气名（墨、大字距）+ 英文小字 + 金短线 + 三候 & 公历（金）+ 诗句（灰）
  · 层级只靠两样东西：金线 #C9A227 和字号

改文案：动 ../_lib/copy.py
改规格：动下面的 PAPER / P / 章头函数

用法：
  python3 build_article.py          # 成稿-可复制.html（base64 自包含，可直粘公众号）
  python3 build_article.py --plain  # 成稿-可读.html（相对路径，便于核对）
"""
import base64
import io
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "_lib")))
import copy as C  # noqa: E402  演示正文

IMGDIR = os.path.join(HERE, "图")

# ── 配色 ──
PAPER = "#FAF6EC"
INK = "#2A2522"
BODY = "#4A4540"
MUTE = "#8A8378"
GOLD = "#C9A227"
FONT = ("'Songti SC','Source Han Serif SC','Noto Serif SC','STSong',"
        "'SimSun',serif")

# ── 排版常量 ──
P = "margin:0 18px;"
PC = "margin:0 18px;text-align:center;"
PI = "margin:0;text-align:center;line-height:0;"
GLUE = "<br>"

SUITE = "节气卷"
COVER = "头图-节气卷.png"
ENDING = "结尾图-节气卷.png"


def data_uri(name, maxw=1400, quality=86):
    """内嵌用的图：按显示宽度压一遍再转 JPEG。

    正文里图片显示宽度只有 677px，直接内嵌 PNG 会做出 7MB 的 HTML，粘进
    公众号编辑器会非常卡。压到显示宽度的两倍左右、JPEG q86，手机上肉眼看
    不出差别，体积降到约 1/8。
    """
    im = Image.open(os.path.join(IMGDIR, name))
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True,
                           progressive=True)
    return "data:image/jpeg;base64,%s" % base64.b64encode(buf.getvalue()).decode("ascii")


def build(plain=False):
    def src(name):
        return ("图/" + name) if plain else data_uri(name)

    def img(name, alt=""):
        return ('<p style="%s"><img src="%s" alt="%s" style="width:100%%;'
                'max-width:100%%;height:auto;display:block;margin:0 auto;"></p>'
                % (PI, src(name), alt))

    def p(text):
        return '<p style="%s">%s</p>' % (P, text)

    def pc(text):
        return '<p style="%s">%s</p>' % (PC, text)

    def span(text, size, color, ls, weight="normal"):
        return ('<span style="font-size:%dpx;color:%s;letter-spacing:%sem;'
                'font-weight:%s;">%s</span>' % (size, color, ls, weight, text))

    def rule(width=44):
        """一条居中金短线。公众号里不能可靠用 border 画细线，用 1px 的 span 更稳。"""
        return ('<p style="%s"><span style="display:inline-block;width:%dpx;'
                'height:1px;background:%s;"></span></p>' % (PC, width, GOLD))

    def gap():
        return '<p style="%s">%s</p>' % (P, GLUE)

    out = []
    a = out.append

    # ── 头图 ──
    a(img(COVER, "二十四节气"))
    a(gap())
    a(pc(span(C.AUTHOR, 12, MUTE, "0.24")))
    a(gap())

    # ── 开场 ──
    for para in C.LEAD:
        a(p(para))
        a(gap())

    # ── 六章，按时间推进 ──
    for cn, en, hou, poem, date, _chip, _txt, paras in C.CHAPTERS:
        a(img("段带-%s.png" % cn, cn))
        a(gap())
        a(pc(span(cn, 30, INK, "0.22", "bold")))
        a(gap())
        a(pc(span(en, 10, MUTE, "0.3")))
        a(rule())          # 金短线紧贴英文小字，不再各留一个空行
        a(gap())
        a(pc(span("%s · %s" % (hou, date), 12, GOLD, "0.22")))
        a(gap())
        a(pc(span(poem, 14, MUTE, "0.16")))
        a(gap())
        for para in paras:
            a(p(para))
            a(gap())

    # ── 收束 ──
    a(p(C.CLOSING))
    a(gap())
    for line in C.ACTIONS:
        a(p(line))
        a(gap())

    # ── 结尾图 + 固定尾部 ──
    a(img(ENDING, "四时有序"))
    a(gap())
    for line in C.FOOTERS:
        a(pc(span(line, 12, MUTE, "0.2")))
        a(gap())

    body = "\n\n  ".join(out).rstrip()

    meta = {
        "paper": PAPER, "bodyc": BODY, "ink": INK, "gold": GOLD, "font": FONT,
        "body": body, "suite": SUITE,
    }
    doc = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(suite)s · 二十四节气新中式排版模板</title>
<style>html,body{margin:0;padding:0;background:#E9E9EC;}</style>
</head>
<body>
<!--
  ============================================================
  「%(suite)s」· 二十四节气新中式排版模板
  ------------------------------------------------------------
  容器    max-width 677px 居中 / 底 %(paper)s 宣纸暖白
  正文    16px / 行高 1.9em / 字距 0.5px / 色 %(bodyc)s（宋体）
  章名    %(ink)s 加粗 / 30px / 字距 0.22em
  金线    %(gold)s，只用于「三候 + 公历」这一行和章头短线
  段间距  靠一个空段撑开，不用 margin-bottom
  时间轴  立春 → 清明 → 夏至 → 白露 → 霜降 → 大雪，六张段带按序推进
  图片    全部 base64 内嵌，全选复制粘进公众号不会丢图

  用法：浏览器打开 成稿-可复制.html → 全选复制 → 粘进公众号编辑器
  ============================================================
-->
<section style="max-width:677px;margin:0 auto;background:%(paper)s;font-family:%(font)s;font-size:16px;letter-spacing:0.5px;line-height:1.9em;color:%(bodyc)s;padding-bottom:44px;">

  %(body)s

</section>
</body>
</html>
""" % meta
    return doc


def guard(html):
    """构建后自检：这几类问题会静默毁掉排版。"""
    bad = []
    if 'font-family:"' in html:
        bad.append('font-family 里出现双引号 → style 属性会被截断')
    if "%%" in html:
        bad.append("残留 %% → 非法 CSS 值")
    if "<div" in html or "class=" in html:
        bad.append("出现 <div> 或 class= → 编辑器会剥掉")
    if "%s" in html:
        bad.append("残留 %s → 格式化没走完")
    return bad


if __name__ == "__main__":
    plain = "--plain" in sys.argv
    name = "成稿-可读.html" if plain else "成稿-可复制.html"
    out = os.path.join(HERE, name)
    doc = build(plain=plain)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print("已生成 %s（%.1f KB）" % (name, os.path.getsize(out) / 1024))
    issues = guard(doc)
    if issues:
        for it in issues:
            print("  x 自检未通过：", it)
        raise SystemExit(1)
    print("  v 构建自检通过")
