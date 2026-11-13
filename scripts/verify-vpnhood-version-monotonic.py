#!/usr/bin/env python3
"""Fail closed when a candidate VpnHood APK does not advance Android versionCode."""
from __future__ import annotations

import re
import sys
from pathlib import Path

EXPECTED_PACKAGE = "cfd.ghostbin.ghostwebvpn"


def read_version_code(path: Path) -> int:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read APK badging file {path}: {exc}") from exc

    package_lines = [line for line in lines if line.startswith("package: ")]
    if len(package_lines) != 1:
        raise ValueError(
            f"{path}: expected exactly one package line, found {len(package_lines)}"
        )

    package_match = re.search(r"\bname='([^']+)'", package_lines[0])
    version_match = re.search(r"\bversionCode='([0-9]+)'", package_lines[0])
    if not package_match or package_match.group(1) != EXPECTED_PACKAGE:
        actual = package_match.group(1) if package_match else "missing"
        raise ValueError(f"{path}: unexpected application ID {actual!r}")
    if not version_match:
        raise ValueError(f"{path}: package line has no numeric versionCode")
    return int(version_match.group(1))


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(
            "Usage: verify-vpnhood-version-monotonic.py <previous-apk-badging> <candidate-apk-badging>",
            file=sys.stderr,
        )
        return 2

    try:
        previous = read_version_code(Path(argv[1]))
        candidate = read_version_code(Path(argv[2]))
    except ValueError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    if candidate <= previous:
        print(
            f"::error::VpnHood Android versionCode must increase: candidate {candidate} <= published {previous}",
            file=sys.stderr,
        )
        return 1

    print(
        f"VpnHood Android versionCode advances from {previous} to {candidate}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
