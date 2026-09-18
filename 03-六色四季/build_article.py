#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套三「六色四季」· 正文模板生成器

版式语言（第三套的差异点是**颜色**）
  · 底：纯白 #FFFFFF，圆角图卡，不用背景色块
  · 时间：每章标题上方一排六个色点，当前节气那个是实心季节色，其余浅灰 ——
         进度条 + 时间轴合一，一眼看出「走到第几个刻度」
  · 四季色取自插画系列的色板：嫩绿 / 烟青 / 碧荷 / 月白 / 丹红 / 雪白；
         月白和雪白太浅，当文字色会看不见，所以标题色用同色系压暗一档的值
  · 金线 #B9963A 只用在序号和章头短线

改文案：动 ../_lib/demo_text.py
用法：
  python3 build_article.py          # 成稿-可复制.html
  python3 build_article.py --plain  # 成稿-可读.html
"""
import base64
import io
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "_lib")))
import demo_text as C  # noqa: E402

IMGDIR = os.path.join(HERE, "图")

PAPER = "#FFFFFF"
INK = "#1B1A18"
BODY = "#3D3B38"
MUTE = "#8E8A84"
GOLD = "#B9963A"
DOT_OFF = "#E6E3DE"        # 未到达的节气色点
FONT = ("-apple-system,'Helvetica Neue','PingFang SC','Hiragino Sans GB',"
        "'Microsoft YaHei',sans-serif")

P = "margin:0 18px;"
PC = "margin:0 18px;text-align:center;"
PI = "margin:0;text-align:center;line-height:0;"
GLUE = "<br>"

SUITE = "六色四季"
COVER = "头图-六色四季.png"
ENDING = "结尾图-六色四季.png"


def data_uri(name, maxw=1400, quality=86):
    """内嵌用的图：压到显示宽度两倍左右再转 JPEG（详见套一同一函数的说明）。"""
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

    def card(name, alt=""):
        """圆角图卡 —— 圆角已经烧进 PNG，不依赖 CSS border-radius。"""
        return ('<p style="%s"><img src="%s" alt="%s" style="width:100%%;'
                'max-width:100%%;height:auto;display:block;margin:0 auto;"></p>'
                % (PI, src(name), alt))

    def p(text):
        return '<p style="%s">%s</p>' % (P, text)

    def pc(text):
        return '<p style="%s">%s</p>' % (PC, text)

    def span(text, size, color, ls, weight="normal", lh=""):
        return ('<span style="font-size:%s;color:%s;letter-spacing:%sem;'
                'font-weight:%s;%s">%s</span>'
                % (size, color, ls, weight, lh, text))

    def dots(idx):
        """六个节气色点，第 idx 个（从 0 数）是实心季节色，其余浅灰。"""
        cells = []
        for j, (_cn, _en, _hou, _poem, _d, chip, txt, _ps) in enumerate(C.CHAPTERS):
            on = (j == idx)
            cells.append(
                '<span style="display:inline-block;width:%dpx;height:%dpx;'
                'border-radius:50%%;background:%s;margin:0 5px;'
                'vertical-align:middle;"></span>'
                % (11 if on else 7, 11 if on else 7, chip if on else DOT_OFF))
        return '<p style="%s">%s</p>' % (PC, "".join(cells))

    def rule(width=30):
        return ('<p style="%s"><span style="display:inline-block;width:%dpx;'
                'height:2px;background:%s;"></span></p>' % (PC, width, GOLD))

    def gap():
        return '<p style="%s">%s</p>' % (P, GLUE)

    out = []
    a = out.append

    # ── 头图 ──
    a(card(COVER, "二十四节气"))
    a(gap())
    a(pc(span(C.AUTHOR, "12.5px", MUTE, "0.2")))
    a(gap())

    # ── 开场 ──
    for para in C.LEAD:
        a(p(para))
        a(gap())

    # ── 六章，按时间推进 ──
    for i, (cn, en, hou, poem, date, chip, txt, paras) in enumerate(C.CHAPTERS):
        a(card("卡带-%s.png" % cn, cn))
        a(gap())
        a(dots(i))                       # 进度：走到第几个刻度
        a(gap())
        a(pc(span("%02d" % (i + 1), "12px", GOLD, "0.3", "600")))
        a(pc(span(cn, "27px", txt, "0.2", "700", "line-height:1.5;")))
        a(rule())
        a(pc(span("%s · %s" % (en.split(" · ")[-1], date), "11.5px", MUTE, "0.12")))
        a(pc(span(hou, "11.5px", MUTE, "0.2")))
        a(gap())
        a(pc(span(poem, "13.5px", txt, "0.18")))
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
    a(card(ENDING, "四时有序"))
    a(gap())
    for line in C.FOOTERS:
        a(pc(span(line, "12px", MUTE, "0.16")))
        a(gap())

    body = "\n\n  ".join(out).rstrip()

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
  容器    max-width 677px 居中 / 底 %(paper)s 纯白
  正文    16px / 行高 1.95em / 字距 0.3px / 色 %(bodyc)s（无衬线）
  图卡    圆角烧进 PNG，不依赖 CSS border-radius（编辑器剥样式也不会变方角）
  时间    每章标题上方六色点，当前节气实心；节气名用该节气的季节色
  四季色  嫩绿 %(c0)s / 烟青 %(c1)s / 碧荷 %(c2)s / 月白 %(c3)s / 丹红 %(c4)s / 雪白 %(c5)s
  图片    全部 base64 内嵌，全选复制粘进公众号不会丢图
  ============================================================
-->
<section style="max-width:677px;margin:0 auto;background:%(paper)s;font-family:%(font)s;font-size:16px;letter-spacing:0.3px;line-height:1.95em;color:%(bodyc)s;padding-bottom:48px;">

  %(body)s

</section>
</body>
</html>
""" % {
        "suite": SUITE, "paper": PAPER, "bodyc": BODY, "font": FONT, "body": body,
        "c0": C.CHAPTERS[0][5], "c1": C.CHAPTERS[1][5], "c2": C.CHAPTERS[2][5],
        "c3": C.CHAPTERS[3][5], "c4": C.CHAPTERS[4][5], "c5": C.CHAPTERS[5][5],
    }
    return doc


def guard(html):
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
