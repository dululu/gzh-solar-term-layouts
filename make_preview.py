#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「三套对照总览」页（预览.html）+ 缩略图。

为什么要这一页：三套模板是同一篇正文的三种版式，横向摆在一起才看得出差别，
不用挨个打开三个 600KB 的 HTML。

用法：python3 make_preview.py
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(HERE, "预览")
SHOT = os.path.join(HERE, "shot.sh")
BASH = "/bin/bash"

SUITES = [
    ("01-节气卷", "节气卷", "宣纸暖白 · 宋体 · 整幅节气段带逐章推进",
     "底 #FAF6EC / 章头居中 / 六张 1260×580 段带 / 金线 #C9A227"),
    ("02-留白笺", "留白笺", "近白底 · 无衬线 · 一律左对齐 · 只留一道山脊线",
     "底 #FDFCF9 / 章头左对齐 + 01·06 序号 / 1400×189 窄带 / 金线 #B9963A"),
    ("03-六色四季", "六色四季", "纯白底 · 圆角图卡 · 六色色点走出时间进度",
     "底 #FFFFFF / 四季色板 / 圆角烧进 PNG / 金线 #B9963A"),
]

FONT = "'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif"


def shots(suite):
    """整页截图（截到 /tmp/jieqi-<suite>/full.png）

    shot.sh 里量页高那步要 Pillow，所以把「当前这个解释器」传给它 ——
    本脚本自己能 import PIL，说明 sys.executable 一定有 Pillow，
    比让 shot.sh 去 PATH 里碰运气稳。
    """
    env = dict(os.environ, PY=os.environ.get("PY") or sys.executable)
    subprocess.run([BASH, SHOT, suite], check=True, cwd=HERE, env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "/tmp/jieqi-%s/full.png" % suite


def save_thumb(src, width, out, pad_color=None):
    im = Image.open(src).convert("RGB")
    im = im.resize((width, max(1, round(im.height * width / im.width))), Image.LANCZOS)
    if pad_color:
        bg = Image.new("RGB", (im.width + 2, im.height + 2), pad_color)
        bg.paste(im, (1, 1))
        im = bg
    im.save(out)
    return im.size


def main():
    os.makedirs(PREV, exist_ok=True)
    cards = []
    for folder, name, tagline, spec in SUITES:
        d = os.path.join(HERE, folder)
        full = shots(folder)
        cover = save_thumb(os.path.join(d, "图", "头图-%s.png" % name), 620,
                           os.path.join(PREV, "%s-头图.png" % name))
        page = save_thumb(full, 232, os.path.join(PREV, "%s-整页.png" % name),
                          (214, 214, 220))
        end = save_thumb(os.path.join(d, "图", "结尾图-%s.png" % name), 470,
                         os.path.join(PREV, "%s-结尾.png" % name))
        cards.append({
            "folder": folder, "name": name, "tagline": tagline, "spec": spec,
            "cover": "%s-头图.png" % name,
            "page": "%s-整页.png" % name,
            "end": "%s-结尾.png" % name,
            "page_h": page[1],
        })
        print("  ", name, "头图", cover, "整页", page, "结尾", end)

    blocks = []
    for c in cards:
        blocks.append("""
  <section class="card">
    <header>
      <h2>%(name)s</h2>
      <p class="tag">%(tagline)s</p>
    </header>
    <div class="shots">
      <div class="page"><img src="预览/%(page)s" alt="整页" style="height:%(ph)dpx;"></div>
      <div class="imgs">
        <img src="预览/%(cover)s" alt="头图">
        <img src="预览/%(end)s" alt="结尾图">
      </div>
    </div>
    <p class="spec">%(spec)s</p>
    <p class="go"><a href="%(folder)s/成稿-可读.html">打开这一套的完整样板 →</a>
       <span>（可复制版：%(folder)s/成稿-可复制.html，直接全选粘进公众号）</span></p>
  </section>""" % dict(c, ph=c["page_h"]))

    doc = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>二十四节气 · 三套排版模板对照</title>
<style>
  body{margin:0;padding:44px 36px 64px;background:#F4F4F6;font-family:%(font)s;
       color:#232323;-webkit-font-smoothing:antialiased;}
  .hd{max-width:1180px;margin:0 auto 34px;}
  .hd h1{margin:0 0 10px;font-size:30px;letter-spacing:0.02em;}
  .hd p{margin:0;font-size:14px;color:#6C6C74;line-height:1.9;}
  .card{max-width:1180px;margin:0 auto 30px;background:#fff;border-radius:14px;
        padding:28px 30px 24px;box-shadow:0 1px 3px rgba(0,0,0,.06);
        border:1px solid #ECECEF;}
  .card h2{margin:0;font-size:21px;letter-spacing:0.04em;}
  .tag{margin:8px 0 0;font-size:13.5px;color:#6C6C74;}
  .shots{display:flex;gap:26px;margin:22px 0 4px;align-items:flex-start;}
  .page{flex:0 0 auto;background:#F0F0F4;border-radius:8px;padding:6px;line-height:0;}
  .page img{display:block;width:232px;height:auto;border-radius:4px;}
  .imgs{flex:1 1 auto;min-width:0;}
  .imgs img{display:block;width:100%%;height:auto;border-radius:8px;
            border:1px solid #EAEAEC;margin-bottom:14px;}
  .imgs img:last-child{margin-bottom:0;}
  .spec{margin:14px 0 0;font-size:12.5px;color:#8A8A92;letter-spacing:0.02em;
        font-family:ui-monospace,Menlo,Consolas,monospace;}
  .go{margin:14px 0 0;font-size:13.5px;}
  .go a{color:#1F4E6E;text-decoration:none;font-weight:600;
        border-bottom:1px solid #C9D8E2;}
  .go span{color:#9A9AA2;margin-left:10px;}
</style></head>
<body>
<div class="hd">
  <h1>二十四节气 · 三套排版模板</h1>
  <p>同一篇正文，三种版式。素材是那套新中式扁平插画（六张物候图），
     三套都把「时间」当主线：立春 → 清明 → 夏至 → 白露 → 霜降 → 大雪。<br>
     每套都有头图、章节分隔图、结尾图三件套，规格见下方。</p>
</div>
%(blocks)s
</body></html>
""" % {"font": FONT, "blocks": "\n".join(blocks)}

    out = os.path.join(HERE, "预览.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print("已生成 预览.html（%.1f KB）" % (os.path.getsize(out) / 1024))


if __name__ == "__main__":
    main()
