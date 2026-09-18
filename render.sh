#!/bin/bash
# 二十四节气排版模板 · 通用出图脚本
#
#   bash render.sh 01-节气卷
#
# 干两件事：跑该套的 gen_html.py 生成头图/结尾图的 HTML，再用无头 Chrome 截图。
# 截图清单从 `_build/shots.tsv` 读，每行三段（制表符分隔）：
#     输入 html 名        窗口宽,高        输出 png 名
#
# 为什么把 Chrome 藏进脚本里跑：直接从前台工具裸调 Chrome，在受限环境下会
# 因自身沙箱起不来而 SIGTRAP（不产文件）；放进前台 shell 脚本、并先做一次
# 8×8 小图探针、需要时自动补 --no-sandbox，就稳定出图。
set -e

SELF="$(cd "$(dirname "$0")" && pwd)"
# 可传套目录名（如 01-节气卷），也可以不带参数 —— 不带参数时就以脚本自己所在的
# 目录为目标，方便把脚本连同「图/  gen_html.py」一起拷进某一篇成稿的目录里直接用。
SUITE="${1:-.}"
DIR="$SELF/$SUITE"
TAG="$(basename "$(cd "$DIR" && pwd)")"
# 挑一个装了 Pillow 的 python3。想指定就设 PY：
#   PY=/path/to/python3 bash render.sh 01-节气卷
pick_py () {
  for c in "${PY:-}" python3 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
    [ -n "$c" ] && command -v "$c" >/dev/null 2>&1 && \
      "$c" -c "import PIL" >/dev/null 2>&1 && { echo "$c"; return; }
  done
  echo python3
}
PY="$(pick_py)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

[ -d "$DIR" ] || { echo "找不到目录：$DIR" >&2; exit 1; }
[ -x "$CHROME" ] || { echo "找不到 Chrome：$CHROME，可设 CHROME= 覆盖" >&2; exit 1; }

echo "① 生成 HTML ..."
"$PY" "$DIR/gen_html.py"

BASE=(--headless=new --disable-gpu --hide-scrollbars
      --force-device-scale-factor=1 --virtual-time-budget=6000)
PROBE="$DIR/_build/.probe.png"

probe () {
  # $1 = 额外参数（"" 或 "--no-sandbox"）。故意不加引号 —— 空值要展开成零个参数。
  local extra="$1"
  local _log
  rm -f "$PROBE"
  _log=$("$CHROME" "${BASE[@]}" $extra --window-size=8,8 --screenshot="$PROBE" \
         "data:text/html,<body style='margin:0;background:%23fff;width:8px;height:8px'></body>" 2>&1) || true
  [ -s "$PROBE" ] && return 0
  rm -f "$PROBE"
  return 1
}

SANDBOX=""
if probe ""; then
  :
elif probe "--no-sandbox"; then
  SANDBOX="--no-sandbox"
  echo "   提示：本机 Chrome 自身沙箱无法启动，已自动改用 --no-sandbox。"
else
  echo "✗ Chrome 起不来，无法截图。" >&2
  exit 1
fi

echo "② 渲染 ..."
OUT="$DIR/图"
mkdir -p "$OUT"
OK=0
FAIL=0
while IFS=$'\t' read -r html wh png; do
  [ -n "$html" ] || continue
  case "$html" in \#*) continue ;; esac
  rm -f "$OUT/$png"
  _log=$("$CHROME" "${BASE[@]}" ${SANDBOX:+$SANDBOX} \
         --window-size="$wh" --screenshot="$OUT/$png" \
         "file://$DIR/_build/$html" 2>&1) || true
  if [ -s "$OUT/$png" ]; then
    echo "   ✓ $png  ($wh)"
    OK=$((OK+1))
  else
    echo "   ✗ $png 渲染失败" >&2
    FAIL=$((FAIL+1))
  fi
done < "$DIR/_build/shots.tsv"
rm -f "$PROBE"

[ "$OK" -gt 0 ] || { echo "✗ 一张都没出来" >&2; exit 1; }
echo "③ 完成：$OK 张成功，$FAIL 张失败 → $OUT"
