#!/usr/bin/env bash
set -euo pipefail

allow_debuggable=false
if [[ "${1:-}" == "--allow-debuggable" ]]; then
  allow_debuggable=true
  shift
fi

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 [--allow-debuggable] <aapt-badging-output-file>" >&2
  exit 2
fi

badging_file="$1"
test -s "$badging_file" || {
  echo "::error::APK badging output is missing or empty: $badging_file" >&2
  exit 1
}

if grep -Fq "application-debuggable" "$badging_file" && [[ "$allow_debuggable" != true ]]; then
  echo "::error::Release APK is debuggable; refusing production release" >&2
  exit 1
fi

if ! grep -Fq "application-label:'GhostWeb VPN'" "$badging_file"; then
  echo "::error::APK application label is not GhostWeb VPN; refusing release" >&2
  exit 1
fi

if [[ "$allow_debuggable" == true ]]; then
  echo "APK manifest is branded GhostWeb VPN; debuggable status accepted for this debug-only check."
else
  echo "APK manifest is not debuggable and branded GhostWeb VPN."
fi
