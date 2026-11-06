#!/usr/bin/env python3
"""Record exact NuGet package provenance for the GhostWeb VpnHood Android client."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

EXPECTED_PACKAGES = {
    "VpnHood.Client": "5.0.616-prerelease",
    "VpnHood.Client.Device.Android": "5.0.616-prerelease",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child_text(parent: ET.Element, name: str) -> str | None:
    for child in parent:
        if local_name(child.tag) == name:
            return (child.text or "").strip()
    return None


def safe_source_host(value: str | None) -> str:
    if not value:
        return "not recorded by NuGet cache metadata"
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"https", "http"} or not parsed.hostname:
        return "non-HTTP source; value withheld"
    host = parsed.hostname.lower()
    if parsed.port and not (
        parsed.scheme.lower() == "https" and parsed.port == 443
    ) and not (parsed.scheme.lower() == "http" and parsed.port == 80):
        host = f"{host}:{parsed.port}"
    return f"{parsed.scheme.lower()}://{host}"


def safe_repository_url(value: str | None) -> str:
    if not value:
        return "not provided in package metadata"
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"https", "http"} or not parsed.hostname:
        return "non-HTTP repository URL; value withheld"
    host = parsed.hostname.lower()
    if parsed.port and not (
        parsed.scheme.lower() == "https" and parsed.port == 443
    ) and not (parsed.scheme.lower() == "http" and parsed.port == 80):
        host = f"{host}:{parsed.port}"
    return urlunsplit(
        (parsed.scheme.lower(), host, parsed.path.rstrip("/"), "", "")
    )


def read_package_references(project: Path) -> dict[str, str]:
    root = ET.parse(project).getroot()
    found: dict[str, str] = {}
    for element in root.iter():
        if local_name(element.tag) != "PackageReference":
            continue
        package_id = element.attrib.get("Include") or element.attrib.get("Update")
        if not package_id:
            continue
        canonical = next(
            (name for name in EXPECTED_PACKAGES if name.lower() == package_id.lower()),
            None,
        )
        if canonical is None:
            continue
        version = element.attrib.get("Version") or child_text(element, "Version")
        if not version:
            raise ValueError(f"PackageReference has no version: {canonical}")
        if canonical in found:
            raise ValueError(f"Duplicate PackageReference: {canonical}")
        found[canonical] = version
    if set(found) != set(EXPECTED_PACKAGES):
        raise ValueError(
            "Expected exactly the two pinned VpnHood PackageReferences; "
            f"found {sorted(found)}"
        )
    for package_id, expected_version in EXPECTED_PACKAGES.items():
        if found[package_id] != expected_version:
            raise ValueError(
                f"{package_id} version changed from reviewed pin "
                f"{expected_version} to {found[package_id]}"
            )
    return found


def inspect_nuspec(
    nupkg: Path, expected_id: str, expected_version: str
) -> tuple[str, str, str]:
    with zipfile.ZipFile(nupkg) as archive:
        nuspecs = [
            name for name in archive.namelist() if name.lower().endswith(".nuspec")
        ]
        if len(nuspecs) != 1:
            raise ValueError(
                f"Expected one nuspec in {nupkg.name}; found {len(nuspecs)}"
            )
        root = ET.fromstring(archive.read(nuspecs[0]))
    metadata = next(
        (element for element in root.iter() if local_name(element.tag) == "metadata"),
        None,
    )
    if metadata is None:
        raise ValueError(f"Missing nuspec metadata in {nupkg.name}")
    package_id = child_text(metadata, "id") or ""
    version = child_text(metadata, "version") or ""
    if package_id.lower() != expected_id.lower() or version.lower() != expected_version.lower():
        raise ValueError(
            f"NuGet package identity mismatch in {nupkg.name}: {package_id} {version}"
        )
    repository = next(
        (element for element in metadata if local_name(element.tag) == "repository"),
        None,
    )
    if repository is None:
        return (
            "not provided in package metadata",
            "not provided in package metadata",
            "not provided",
        )
    return (
        safe_repository_url(repository.attrib.get("url")),
        repository.attrib.get("commit") or "not provided in package metadata",
        repository.attrib.get("type") or "not provided",
    )


def record_package(
    package_id: str, version: str, packages_root: Path
) -> list[str]:
    package_dir = packages_root / package_id.lower() / version.lower()
    metadata_path = package_dir / ".nupkg.metadata"
    if not metadata_path.is_file():
        raise ValueError(
            f"NuGet restore metadata is missing for {package_id} {version}"
        )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    content_hash = str(metadata.get("contentHash", "")).strip()
    if not content_hash:
        raise ValueError(f"NuGet contentHash is missing for {package_id} {version}")

    nupkgs = sorted(package_dir.glob("*.nupkg"))
    if len(nupkgs) != 1:
        raise ValueError(
            f"Expected one restored .nupkg for {package_id} {version}; found {len(nupkgs)}"
        )
    nupkg = nupkgs[0]
    package_bytes = nupkg.read_bytes()
    actual_content_hash = base64.b64encode(
        hashlib.sha512(package_bytes).digest()
    ).decode("ascii")
    sha512_path = package_dir / f"{nupkg.name}.sha512"
    cached_hash = (
        sha512_path.read_text(encoding="utf-8").strip()
        if sha512_path.is_file()
        else "missing"
    )
    if content_hash != cached_hash:
        raise ValueError(
            f"NuGet metadata/cache hash mismatch for {package_id} {version}: "
            f"metadata={content_hash}; cache={cached_hash}; "
            f"recomputed_sha512={actual_content_hash}"
        )
    if actual_content_hash != content_hash:
        raise ValueError(
            f"Recomputed .nupkg SHA-512 differs for {package_id} {version}: "
            f"metadata={content_hash}; cache={cached_hash}; "
            f"recomputed_sha512={actual_content_hash}"
        )

    repository_url, repository_commit, repository_type = inspect_nuspec(
        nupkg, package_id, version
    )
    return [
        f"Package: {package_id}",
        f"Version: {version}",
        f"Package file: {nupkg.name}",
        f"Package SHA-256: {hashlib.sha256(package_bytes).hexdigest()}",
        f"NuGet contentHash (SHA-512/Base64): {actual_content_hash}",
        f"NuGet source host: {safe_source_host(metadata.get('source'))}",
        f"Nuspec repository type: {repository_type}",
        f"Nuspec repository URL: {repository_url}",
        f"Nuspec repository commit: {repository_commit}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument(
        "--packages-dir", type=Path, default=Path.home() / ".nuget" / "packages"
    )
    parser.add_argument("--upstream-revision-file", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        references = read_package_references(args.project)
        lines = [
            "GhostWeb VpnHood Android NuGet package provenance",
            "Generated from the exact NuGet global-package cache after dotnet restore.",
            "",
        ]
        if args.upstream_revision_file:
            revision = args.upstream_revision_file.read_text(encoding="utf-8").strip()
            if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
                raise ValueError("Pinned upstream revision file is missing or invalid")
            lines.extend(
                [
                    f"Separate VpnHood upstream source checkout: {revision.lower()}",
                    "The upstream checkout is a separate browser-UI/license input; it is not assumed to be the source commit for the NuGet package bytes below.",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "Separate VpnHood upstream source checkout: not included in this workflow.",
                    "This report records the standalone GhostWeb client's restored NuGet inputs only.",
                    "",
                ]
            )

        for package_id, version in references.items():
            lines.extend(record_package(package_id, version, args.packages_dir))
            lines.append("")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "\n".join(lines).rstrip() + "\n", encoding="utf-8"
        )
        print(
            f"Recorded and verified NuGet provenance for {len(references)} pinned packages."
        )
        return 0
    except (
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
        zipfile.BadZipFile,
        ET.ParseError,
    ) as exc:
        print(f"::error::NuGet provenance verification failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
