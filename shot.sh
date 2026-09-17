#!/bin/bash
# 二十四节气排版模板 · 整页截图核对
#
#   bash shot.sh 01-节气卷
#
# 量真实页面高度 → 按该高度整页截图 → 切成若干段方便逐段看。
#
# 两个必须踩过的坑：
#   1) 页面放在 /tmp 子目录时，正文里的相对路径图片会全 404（截图里只剩 alt 文字），
#      所以必须把 图/ 一起拷过去。
#   2) 高度不能写死。窗口宽度决定换行、换行决定高度，量高和截图必须同宽。
set -e

SELF="$(cd "$(dirname "$0")" && pwd)"
SUITE="${1:?用法: bash shot.sh <套目录名>}"
DIR="$SELF/$SUITE"
# 挑一个装了 Pillow 的 python3（切片那步要用）。想指定就设 PY：
#   PY=/path/to/python3 bash shot.sh 01-节气卷
pick_py () {
  for c in "${PY:-}" python3 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
    [ -n "$c" ] && command -v "$c" >/dev/null 2>&1 && \
      "$c" -c "import PIL" >/dev/null 2>&1 && { echo "$c"; return; }
  done
  echo python3
}
PY="$(pick_py)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
TMP="/tmp/jieqi-${SUITE}"

SEG=2200
W=677

rm -rf "$TMP"
mkdir -p "$TMP"
cp "$DIR/成稿-可读.html" "$TMP/page.html"
cp -R "$DIR/图" "$TMP/图"
cat >> "$TMP/page.html" <<'EOF'
<script>document.title = document.documentElement.scrollHeight + 'px';</script>
EOF

H=$("$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
     --virtual-time-budget=8000 --dump-dom "file://$TMP/page.html" 2>/dev/null \
     | grep -o '<title>[0-9]*px</title>' | head -1 | grep -o '[0-9]*')
[ -n "$H" ] || { echo "量高失败" >&2; exit 1; }
echo "页面高度 ${H} px，宽 ${W}"

rm -f "$TMP/full.png"
_log=$("$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --window-size="$W,$H" --virtual-time-budget=8000 \
  --screenshot="$TMP/full.png" "file://$TMP/page.html" 2>&1) || true
[ -s "$TMP/full.png" ] || { echo "截图失败" >&2; exit 1; }
echo "整页截图 $(wc -c < "$TMP/full.png" | tr -d ' ') bytes"

"$PY" - "$TMP/full.png" "$SEG" "$TMP" "$W" <<'PYEOF'
import sys
from PIL import Image
src, seg, tmp, w = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
im = Image.open(src).convert("RGB")
print("  实际尺寸", im.size)
n = (im.size[1] + seg - 1) // seg
for i in range(n):
    box = (0, i * seg, im.size[0], min(im.size[1], (i + 1) * seg))
    im.crop(box).save("%s/part-%d.png" % (tmp, i + 1))
# 缩略版：一眼看整篇节奏
thumb = im.resize((max(1, w // 3), max(1, im.size[1] // 3)), Image.LANCZOS)
thumb.save("%s/thumb.png" % tmp)
print("  切了", n, "段 →", tmp)
PYEOF
