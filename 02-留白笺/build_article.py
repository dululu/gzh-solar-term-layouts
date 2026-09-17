#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套二「留白笺」· 正文模板生成器

版式语言（和套一正好相反：套一是居中 + 宋体 + 整幅画，套二一律左对齐 + 无衬线 + 一条窄带）
  · 底：近白 #FDFCF9，不用色块、不用边框
  · 全部左对齐，靠留白和字号分层次，不用居中排版
  · 时间：每章一条「01 / 06」序号 + 公历日期；分隔是 1400×189 的窄带，
         只留一道山脊线，左右两端渐隐成云带
  · 金线 #B9963A 只出现在序号、章头短线两处

改文案：动 ../_lib/copy.py
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
import copy as C  # noqa: E402

IMGDIR = os.path.join(HERE, "图")

PAPER = "#FDFCF9"
INK = "#1F1E1C"
BODY = "#3D3B38"
MUTE = "#8C8880"
GOLD = "#B9963A"
FONT = ("-apple-system,'Helvetica Neue','PingFang SC','Hiragino Sans GB',"
        "'Microsoft YaHei',sans-serif")

P = "margin:0 26px;"
PC = "margin:0 26px;text-align:center;"
PI = "margin:0;text-align:center;line-height:0;"
GLUE = "<br>"

SUITE = "留白笺"
COVER = "头图-留白笺.png"
ENDING = "结尾图-留白笺.png"


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

    def img(name, alt=""):
        return ('<p style="%s"><img src="%s" alt="%s" style="width:100%%;'
                'max-width:100%%;height:auto;display:block;margin:0 auto;"></p>'
                % (PI, src(name), alt))

    def p(text, style=P):
        return '<p style="%s">%s</p>' % (style, text)

    def span(text, size, color, ls, weight="normal", lh=""):
        return ('<span style="font-size:%s;color:%s;letter-spacing:%sem;'
                'font-weight:%s;%s">%s</span>'
                % (size, color, ls, weight, lh, text))

    def rule(width=34):
        """左对齐金短线：公众号里用 1px 的 inline-block 比 border 稳。"""
        return ('<p style="%s"><span style="display:inline-block;width:%dpx;'
                'height:1px;background:%s;"></span></p>' % (P, width, GOLD))

    def gap():
        return '<p style="%s">%s</p>' % (P, GLUE)

    out = []
    a = out.append

    # ── 头图 ──
    a(img(COVER, "二十四节气"))
    a(gap())
    a(p(span(C.AUTHOR, "12.5px", MUTE, "0.2")))

    # ── 开场 ──
    a(gap())
    for para in C.LEAD:
        a(p(para))
        a(gap())

    # ── 时间轴行：把六个刻度先摆出来，读者带着时间线往下读 ──
    axis = " · ".join(c[0] for c in C.CHAPTERS)
    a(rule(30))
    a(gap())
    a(p(span(axis, "12px", GOLD, "0.22")))
    a(p(span("六个刻度，一条时间线", "12px", MUTE, "0.1")))
    a(gap())

    # ── 六章，按时间推进 ──
    for i, (cn, en, hou, poem, date, _chip, _txt, paras) in enumerate(C.CHAPTERS, 1):
        a(img("窄带-%s.png" % cn, cn))
        a(gap())
        a(p(span("%02d / %02d" % (i, len(C.CHAPTERS)), "11px", GOLD, "0.34", "600")))
        a(p(span(cn, "25px", INK, "0.2", "700", "line-height:1.6;")))
        a(p(span("%s · %s" % (hou, date), "12px", MUTE, "0.08")))
        a(rule())
        a(p(span(poem, "13.5px", MUTE, "0.18")))
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
        a(p(span(line, "12px", MUTE, "0.16")))
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
  容器    max-width 677px 居中 / 底 %(paper)s 近白
  正文    16px / 行高 1.95em / 字距 0.3px / 色 %(bodyc)s（无衬线）
  排版    一律左对齐，靠留白分层，不用居中
  时间    每章「01 / 06」序号 + 公历日期；分隔是只留山脊线的窄带
  金线    %(gold)s，只用于序号与章头短线
  图片    全部 base64 内嵌，全选复制粘进公众号不会丢图
  ============================================================
-->
<section style="max-width:677px;margin:0 auto;background:%(paper)s;font-family:%(font)s;font-size:16px;letter-spacing:0.3px;line-height:1.95em;color:%(bodyc)s;padding-bottom:48px;">

  %(body)s

</section>
</body>
</html>
""" % {
        "suite": SUITE, "paper": PAPER, "bodyc": BODY, "gold": GOLD, "font": FONT,
        "body": body,
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
