#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套一「节气卷」· 生成头图 / 结尾图的 HTML + 截图清单

为什么走 HTML 而不是 Pillow 直接画：中文标题要用思源宋体的重字重，还要控字距和
行高，浏览器渲染比 Pillow 去翻字体文件稳得多。

改文案：动下面的 TITLE / SUB / FOOT_* 常量。
出图：bash ../render.sh 01-节气卷
"""
import base64
import mimetypes
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(HERE, "图")
BUILD = os.path.join(HERE, "_build")

PAPER = "#FAF6EC"
GOLD = "#C9A227"
INK = "#2A2522"
MUTE = "#8A8378"

TITLE = "二十四节气"
SUB = "一 年 二 十 四 个 刻 度"

FOOT_TITLE = "四 时 有 序"
FOOT_SUB = "从立春到大雪，走完一圈四季"

FONT = ("'Source Han Serif SC','Noto Serif SC','Songti SC','STSong',"
        "'SimSun',serif")


def uri(name):
    path = os.path.join(IMGDIR, name)
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode("ascii"))


def cover():
    """头图 1800×766（2.35:1）：宣纸底 + 居中标题 + 底部金线远山带。"""
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;}
  .cover{width:1800px;height:766px;position:relative;overflow:hidden;
         background:%(paper)s;font-family:%(font)s;}
  .band{position:absolute;left:0;bottom:0;width:1800px;line-height:0;}
  .band img{width:100%%;height:auto;display:block;}
  .txt{position:absolute;left:0;right:0;top:74px;text-align:center;z-index:2;}
  .t1{font-size:146px;font-weight:900;color:%(ink)s;
      letter-spacing:0.1em;text-indent:0.1em;line-height:1.08;}
  .rule{width:132px;height:2px;background:%(gold)s;margin:34px auto 26px;}
  .t2{font-size:27px;color:%(mute)s;letter-spacing:0.32em;text-indent:0.32em;font-weight:400;}
</style></head>
<body><div class="cover">
  <div class="txt">
    <div class="t1">%(title)s</div>
    <div class="rule"></div>
    <div class="t2">%(sub)s</div>
  </div>
  <div class="band"><img src="%(band)s" alt=""></div>
</div></body></html>""" % {
        "paper": PAPER, "gold": GOLD, "ink": INK, "mute": MUTE, "font": FONT,
        "title": TITLE, "sub": SUB, "band": uri("头带-霜降.png"),
    }


def end():
    """结尾图 1354×600：宣纸底 + 金线 + 收尾语 + 底部大雪带。"""
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;}
  .end{width:1354px;height:600px;position:relative;overflow:hidden;
       background:%(paper)s;font-family:%(font)s;}
  /* band 约 376px 高、贴在底边，会盖住文字区下半 → 文字层必须显式提到上层 */
  .band{position:absolute;left:0;bottom:0;width:1354px;line-height:0;z-index:1;}
  .band img{width:100%%;height:auto;display:block;}
  .txt{position:absolute;left:0;right:0;top:96px;text-align:center;z-index:2;}
  .t1{font-size:62px;font-weight:700;color:%(ink)s;
      letter-spacing:0.16em;text-indent:0.16em;line-height:1.2;}
  .rule{width:88px;height:2px;background:%(gold)s;margin:28px auto 24px;}
  .t2{font-size:21px;color:%(mute)s;letter-spacing:0.2em;text-indent:0.2em;font-weight:400;}
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
    ("cover.html", "1800,766", "头图-节气卷.png"),
    ("end.html", "1354,600", "结尾图-节气卷.png"),
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
