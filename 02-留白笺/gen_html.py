#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套二「留白笺」· 生成头图 / 结尾图的 HTML + 截图清单

版式语言：近白底、无衬线、全部左对齐、一条细金线，其余交给留白。
出图：bash ../render.sh 02-留白笺
"""
import base64
import mimetypes
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(HERE, "图")
BUILD = os.path.join(HERE, "_build")

PAPER = "#FDFCF9"
GOLD = "#B9963A"
INK = "#1F1E1C"
MUTE = "#8C8880"

BRAND = "小铭说"
TITLE = "二十四节气"
SUB = "一年二十四个刻度"
NOTE = "SEASONAL NOTES"

FOOT_TITLE = "四时有 序"
FOOT_SUB = "从立春到大雪，走完一圈四季"

FONT = ("-apple-system,'Helvetica Neue','PingFang SC','Hiragino Sans GB',"
        "'Microsoft YaHei',sans-serif")


def uri(name):
    path = os.path.join(IMGDIR, name)
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode("ascii"))


def cover():
    """头图 1800×766（2.35:1）：近白底 + 左侧标题组 + 底部山脊带。"""
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;}
  .cover{width:1800px;height:766px;position:relative;overflow:hidden;
         background:%(paper)s;font-family:%(font)s;}
  .band{position:absolute;left:0;bottom:0;width:1800px;line-height:0;}
  .band img{width:100%%;height:auto;display:block;}
  .txt{position:absolute;left:130px;top:118px;z-index:2;}
  .note{font-size:20px;color:%(gold)s;letter-spacing:0.42em;font-weight:600;}
  .t1{font-size:132px;font-weight:800;color:%(ink)s;letter-spacing:0.1em;
      line-height:1.16;margin-top:34px;}
  .rule{width:86px;height:2px;background:%(gold)s;margin:40px 0 30px;}
  .t2{font-size:27px;color:%(mute)s;letter-spacing:0.16em;}
  .brand{position:absolute;right:130px;top:126px;text-align:right;z-index:2;}
  .brand .n{font-size:23px;color:%(ink)s;letter-spacing:0.34em;font-weight:600;}
  .brand .s{font-size:15px;color:%(mute)s;letter-spacing:0.3em;margin-top:14px;}
</style></head>
<body><div class="cover">
  <div class="txt">
    <div class="note">%(note)s</div>
    <div class="t1">%(title)s</div>
    <div class="rule"></div>
    <div class="t2">%(sub)s</div>
  </div>
  <div class="brand"><div class="n">%(brand)s</div><div class="s">二十四节气 · 物候插画</div></div>
  <div class="band"><img src="%(band)s" alt=""></div>
</div></body></html>""" % {
        "paper": PAPER, "gold": GOLD, "ink": INK, "mute": MUTE, "font": FONT,
        "note": NOTE, "title": TITLE, "sub": SUB, "brand": BRAND,
        "band": uri("头带-霜降.png"),
    }


def end():
    """结尾图 1354×560：近白底 + 居中细字 + 底部山脊带。"""
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;}
  .end{width:1354px;height:560px;position:relative;overflow:hidden;
       background:%(paper)s;font-family:%(font)s;}
  /* band 约 300px 高、贴底边，会盖住文字区下半 → 文字层显式提到上层 */
  .band{position:absolute;left:0;bottom:0;width:1354px;line-height:0;z-index:1;}
  .band img{width:100%%;height:auto;display:block;}
  .txt{position:absolute;left:0;right:0;top:104px;text-align:center;z-index:2;}
  .t1{font-size:54px;font-weight:700;color:%(ink)s;letter-spacing:0.22em;
      text-indent:0.22em;line-height:1.2;}
  .rule{width:64px;height:2px;background:%(gold)s;margin:30px auto 24px;}
  .t2{font-size:20px;color:%(mute)s;letter-spacing:0.16em;}
</style></head>
<body><div class="end">
  <div class="txt">
    <div class="t1">%(title)s</div>
    <div class="rule"></div>
    <div class="t2">%(sub)s</div>
  </div>
  <div class="band"><img src="%(band)s" alt=""></div>
</div></body></html>""" % {
        "paper": PAPER, "gold": GOLD, "ink": INK, "mute": MUTE, "font": FONT,
        "title": FOOT_TITLE, "sub": FOOT_SUB, "band": uri("尾带-大雪.png"),
    }


SHOTS = [
    ("cover.html", "1800,766", "头图-留白笺.png"),
    ("end.html", "1354,560", "结尾图-留白笺.png"),
]

if __name__ == "__main__":
    os.makedirs(BUILD, exist_ok=True)
    for name, html in (("cover.html", cover()), ("end.html", end())):
        with open(os.path.join(BUILD, name), "w", encoding="utf-8") as fh:
            fh.write(html)
        print("   ", name)
    with open(os.path.join(BUILD, "shots.tsv"), "w", encoding="utf-8") as fh:
        for row in SHOTS:
            fh.write("\t".join(row) + "\n")
    print("    shots.tsv")
