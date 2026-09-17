#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
套三「六色四季」· 生成头图 / 结尾图的 HTML + 截图清单

版式语言：纯白底 + 圆角图卡 + 六色色板，用颜色表达四季、用色点表达进度。
出图：bash ../render.sh 03-六色四季
"""
import base64
import mimetypes
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(HERE, "图")
BUILD = os.path.join(HERE, "_build")

PAPER = "#FFFFFF"
INK = "#1B1A18"
MUTE = "#8E8A84"
GOLD = "#B9963A"

BRAND = "小铭说"
TITLE = "二十四节气"
SUB = "一年二十四个刻度"

FOOT_TITLE = "四 时 有 序"
FOOT_SUB = "从立春到大雪，走完一圈四季"

FONT = ("-apple-system,'Helvetica Neue','PingFang SC','Hiragino Sans GB',"
        "'Microsoft YaHei',sans-serif")

# 六色 = 六个节气的季节色（取自插画系列的四季色板）
# 大雪那支原值是雪白 #F2F4F5，铺在白底上等于没有，展示时换成加深的雪灰。
CHIPS = ["#A8C66C", "#7E9E9A", "#3F8E7E", "#CDE3E6", "#C0563E", "#CFD6DA"]


def uri(name):
    path = os.path.join(IMGDIR, name)
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode("ascii"))


def cover():
    """头图 1800×766：纯白底 + 左侧标题组 + 右上六色竖条 + 底部圆角图卡。"""
    chips = "".join(
        '<span style="display:inline-block;width:26px;height:120px;'
        'background:%s;margin-left:10px;vertical-align:top;"></span>' % c
        for c in CHIPS)
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;}
  .cover{width:1800px;height:766px;position:relative;overflow:hidden;
         background:%(paper)s;font-family:%(font)s;}
  .txt{position:absolute;left:124px;top:100px;z-index:2;}
  .t1{font-size:126px;font-weight:800;color:%(ink)s;letter-spacing:0.08em;
      line-height:1.16;}
  .rule{width:74px;height:3px;background:%(gold)s;margin:38px 0 28px;}
  .t2{font-size:26px;color:%(mute)s;letter-spacing:0.14em;}
  .chips{position:absolute;right:120px;top:118px;z-index:2;line-height:0;}
  .brand{position:absolute;right:124px;bottom:420px;text-align:right;z-index:2;}
  .brand .n{font-size:22px;color:%(ink)s;letter-spacing:0.32em;font-weight:600;}
  .brand .s{font-size:14px;color:%(mute)s;letter-spacing:0.26em;margin-top:12px;}
  .card{position:absolute;left:120px;bottom:56px;width:1560px;line-height:0;z-index:1;}
  .card img{width:100%%;height:auto;display:block;}
</style></head>
<body><div class="cover">
  <div class="txt">
    <div class="t1">%(title)s</div>
    <div class="rule"></div>
    <div class="t2">%(sub)s</div>
  </div>
  <div class="chips">%(chips)s</div>
  <div class="brand"><div class="n">%(brand)s</div><div class="s">二十四节气 · 物候插画</div></div>
  <div class="card"><img src="%(card)s" alt=""></div>
</div></body></html>""" % {
        "paper": PAPER, "ink": INK, "mute": MUTE, "gold": GOLD, "font": FONT,
        "title": TITLE, "sub": SUB, "brand": BRAND, "chips": chips,
        "card": uri("头卡-霜降.png"),
    }


def end():
    """结尾图 1354×620：纯白底 + 居中六色条 + 居中细字 + 底部圆角图卡。"""
    # 6 段 × 72px + 5 个 10px 间隙 = 482px，居中摆；每段描一圈浅边框，
    # 否则月白 / 雪灰两支在白底上直接就看不见了。
    chips = "".join(
        '<span style="display:inline-block;width:70px;height:10px;'
        'background:%s;border:1px solid #E3DFD6;margin:0 5px;'
        'vertical-align:top;"></span>' % c for c in CHIPS)
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;}
  .end{width:1354px;height:620px;position:relative;overflow:hidden;
       background:%(paper)s;font-family:%(font)s;}
  .chips{position:absolute;left:0;right:0;top:76px;text-align:center;line-height:0;}
  .txt{position:absolute;left:0;right:0;top:132px;text-align:center;z-index:2;}
  .t1{font-size:52px;font-weight:700;color:%(ink)s;letter-spacing:0.22em;
      text-indent:0.22em;line-height:1.24;}
  .rule{width:60px;height:3px;background:%(gold)s;margin:28px auto 22px;}
  .t2{font-size:19px;color:%(mute)s;letter-spacing:0.16em;}
  .card{position:absolute;left:90px;bottom:52px;width:1174px;line-height:0;z-index:1;}
  .card img{width:100%%;height:auto;display:block;}
</style></head>
<body><div class="end">
  <div class="chips">%(chips)s</div>
  <div class="txt">
    <div class="t1">%(title)s</div>
    <div class="rule"></div>
    <div class="t2">%(sub)s</div>
  </div>
  <div class="card"><img src="%(card)s" alt=""></div>
</div></body></html>""" % {
        "paper": PAPER, "ink": INK, "mute": MUTE, "gold": GOLD, "font": FONT,
        "title": FOOT_TITLE, "sub": FOOT_SUB, "chips": chips,
        "card": uri("尾卡-大雪.png"),
    }


SHOTS = [
    ("cover.html", "1800,766", "头图-六色四季.png"),
    ("end.html", "1354,620", "结尾图-六色四季.png"),
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
