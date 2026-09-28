#!/usr/bin/env bash
# 正文机检。用法：bash 工具/检查.sh 正文/第01章*.md [更多文件]
# ✗ 必须修改；△ 逐条判断。

export LC_ALL=C.UTF-8
dir="$(cd "$(dirname "$0")" && pwd)"
banned="$dir/禁用词.txt"
fail=0

count() { grep -oE "$1" "$2" | wc -l | tr -d ' '; }

for f in "$@"; do
  echo "== $f"

  chars=$(tr -d '[:space:]#*>-' < "$f" | wc -m | tr -d ' ')
  if [ "$chars" -lt 4000 ] || [ "$chars" -gt 6500 ]; then
    echo "△ 字数 $chars（要求 4000～6000）"
  else
    echo "  字数 $chars"
  fi

  p='不是[^。！？]{0,24}[，。；,][[:space:]]*(而|就|只)?是|与其说[^。！？]{0,20}不如说'
  n=$(count "$p" "$f")
  if [ "$n" -gt 1 ]; then
    echo "✗ 「不是…是/而是」「与其说…不如说」共 $n 处（上限 1）："
    grep -nE "$p" "$f" | sed 's/^/    /'
    fail=1
  fi

  n=$(count '像是[^。！？]{0,30}又像是' "$f")
  if [ "$n" -gt 1 ]; then echo "✗ 「像是…又像是」$n 处（上限 1）"; fail=1; fi

  n=$(count '说不上来|说不清' "$f")
  if [ "$n" -gt 0 ]; then echo "✗ 「说不上来/说不清」$n 处（禁用）"; grep -nE '说不上来|说不清' "$f" | sed 's/^/    /'; fail=1; fi

  n=$(count '后来我才知道|很久以后' "$f")
  if [ "$n" -gt 1 ]; then echo "✗ 倒叙提示 $n 处（上限 1）"; fail=1; fi

  n=$(count '——' "$f")
  if [ "$n" -gt 15 ]; then echo "△ 破折号 $n 处（上限 15）"; fi

  n=$(grep -cE '^\s*[0-9]+[.、]' "$f")
  if [ "$n" -gt 0 ]; then echo "✗ 数字编号列表 $n 行（正文禁用）"; fail=1; fi

  while IFS= read -r w; do
    w="${w%$'\r'}"
    [ -z "$w" ] && continue
    if grep -q "$w" "$f"; then
      echo "✗ 禁用词「$w」："
      grep -n "$w" "$f" | sed 's/^/    /'
      fail=1
    fi
  done < "$banned"

  while read -r w cap; do
    w="${w%$'\r'}"; cap="${cap%$'\r'}"
    case "$w" in ''|\#*) continue;; esac
    c=$(grep -o "$w" "$f" | wc -l | tr -d ' ')
    if [ "$c" -gt "$cap" ]; then echo "△ 「$w」出现 $c 次（上限 $cap），换说法或删掉"; fi
  done < "$dir/高频词.txt"

  n=$(grep -cE '^[^「」『』“”"]{1,12}[。！？…]+$' "$f")
  if [ "$n" -gt 25 ]; then echo "△ 短句单独成段 $n 处（建议不超过 25）"; fi

  talk=$(grep -oE '“[^”]*”|"[^"]*"|『[^』]*』' "$f" | tr -d '[:space:]' | wc -m | tr -d ' ')
  if [ "$chars" -gt 0 ]; then
    pct=$((talk * 100 / chars))
    if [ "$pct" -lt 25 ]; then echo "△ 对话占比约 ${pct}%（目标 30～50%）"; else echo "  对话占比约 ${pct}%"; fi
  fi
done

[ $fail -eq 0 ] && echo "通过" || { echo "未通过"; exit 1; }
