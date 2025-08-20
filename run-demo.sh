#!/usr/bin/env bash
set -euo pipefail
python src/main.py --user "$USER_UPN" --top "${TOP:-50}" \
  --category "${CATEGORY:-Suspect-IOC}" --ensure-category \
  ${SUMMARY_TO:+--summary-to "$SUMMARY_TO"}
