#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-iocs.txt}"
curl -fsSL https://urlhaus.abuse.ch/downloads/csv_recent/ \
 | grep -v '^#' | awk -F',' '{print $3}' \
 | sed -E 's~^[^/]*//~~' | awk -F'/' '{print $1}' \
 | sed 's/^\*\.//' | tr '[:upper:]' '[:lower:]' \
 | grep -E '^[a-z0-9.-]+\.[a-z]{2,}$' > "$OUT.tmp"

curl -fsSL https://feodotracker.abuse.ch/downloads/ipblocklist.txt \
 | grep -v '^#' | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' >> "$OUT.tmp"

sort -u "$OUT.tmp" > "$OUT"
rm -f "$OUT.tmp"
echo "Wrote $(wc -l < "$OUT") IoCs to $OUT"
