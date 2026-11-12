#!/usr/bin/env bash
# ChengziCV 版本检查：24 小时内最多联网一次，有新版时输出一行用户提醒。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_VERSION="${1:-$(cat "$SCRIPT_DIR/../version.txt" 2>/dev/null | tr -d '[:space:]')}"
CACHE_DIR="$HOME/.chengzicv"
CACHE_FILE="$CACHE_DIR/update_check_at"
CACHE_TTL=86400

# 两个源按顺序尝试：国内访问 GitHub raw 常被限速，失败时换 jsDelivr 镜像。
# 设置 CHENGZICV_UPDATE_URL 可指向自建镜像或本地文件，便于测试。
REMOTE_URLS=(
  "${CHENGZICV_UPDATE_URL:-https://raw.githubusercontent.com/chengzicv/chengzicv-career-skills/main/UPDATE.json}"
  "https://cdn.jsdelivr.net/gh/chengzicv/chengzicv-career-skills@main/UPDATE.json"
)

SEMVER='(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)'

if [[ ! "$LOCAL_VERSION" =~ ^${SEMVER}$ ]]; then
  exit 0
fi

NOW="$(date +%s)"
if [ -f "$CACHE_FILE" ]; then
  LAST_CHECK="$(tr -d '[:space:]' < "$CACHE_FILE" 2>/dev/null || true)"
  if [[ "$LAST_CHECK" =~ ^[0-9]+$ ]] && [ "$NOW" -ge "$LAST_CHECK" ] && [ $((NOW - LAST_CHECK)) -lt "$CACHE_TTL" ]; then
    exit 0
  fi
fi

mkdir -p "$CACHE_DIR" 2>/dev/null || exit 0
printf '%s\n' "$NOW" > "$CACHE_FILE" 2>/dev/null || exit 0

PAYLOAD=""
for url in "${REMOTE_URLS[@]}"; do
  PAYLOAD="$(curl -fsS --max-time 5 "$url" 2>/dev/null || true)"
  [ -n "$PAYLOAD" ] && break
done
[ -n "$PAYLOAD" ] || exit 0

parse_with_python() {
  python3 -c '
import json, re, sys
semver = r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
try:
    data = json.load(sys.stdin)
    version = data.get("version", "")
    notice = data.get("notice", "")
    edition = data.get("edition", "")
    if not isinstance(version, str) or not re.fullmatch(semver, version):
        raise ValueError
    if not isinstance(notice, str) or not 1 <= len(notice.strip()) <= 80 or any(ch in notice for ch in "\r\n\t"):
        raise ValueError
    if isinstance(edition, bool) or not isinstance(edition, int) or edition < 0:
        edition = 0
    print(f"{version}\t{edition}\t{notice.strip()}", end="")
except Exception:
    sys.exit(1)
'
}

parse_with_node() {
  node -e '
let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", chunk => raw += chunk);
process.stdin.on("end", () => {
  try {
    const data = JSON.parse(raw);
    const version = data.version;
    const notice = data.notice;
    const semver = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/;
    if (typeof version !== "string" || !semver.test(version)) process.exit(1);
    if (typeof notice !== "string" || notice.trim().length < 1 || notice.trim().length > 80 || /[\r\n\t]/.test(notice)) process.exit(1);
    const edition = Number.isInteger(data.edition) && data.edition >= 0 ? data.edition : 0;
    process.stdout.write(`${version}\t${edition}\t${notice.trim()}`);
  } catch (_) {
    process.exit(1);
  }
});
'
}

if command -v python3 >/dev/null 2>&1; then
  PARSED="$(printf '%s' "$PAYLOAD" | parse_with_python 2>/dev/null || true)"
elif command -v node >/dev/null 2>&1; then
  PARSED="$(printf '%s' "$PAYLOAD" | parse_with_node 2>/dev/null || true)"
else
  exit 0
fi

[[ "$PARSED" == *$'\t'* ]] || exit 0
REMOTE_VERSION="${PARSED%%$'\t'*}"
REST="${PARSED#*$'\t'}"
REMOTE_EDITION="${REST%%$'\t'*}"
NOTICE="${REST#*$'\t'}"

version_is_higher() {
  local remote_major remote_minor remote_patch local_major local_minor local_patch
  IFS=. read -r remote_major remote_minor remote_patch <<< "$1"
  IFS=. read -r local_major local_minor local_patch <<< "$2"
  if ((10#$remote_major != 10#$local_major)); then
    ((10#$remote_major > 10#$local_major))
  elif ((10#$remote_minor != 10#$local_minor)); then
    ((10#$remote_minor > 10#$local_minor))
  else
    ((10#$remote_patch > 10#$local_patch))
  fi
}

if version_is_higher "$REMOTE_VERSION" "$LOCAL_VERSION"; then
  if [[ "$REMOTE_EDITION" =~ ^[0-9]+$ ]] && [ "$((10#$REMOTE_EDITION))" -gt 0 ]; then
    printf 'ChengziCV 第 %s 版：%s 回复 1，我现在帮你更新。\n' "$((10#$REMOTE_EDITION))" "$NOTICE"
  else
    printf 'ChengziCV 新版本：%s 回复 1，我现在帮你更新。\n' "$NOTICE"
  fi
fi
