# Security Policy

GhostWeb VPN is under active development. Treat a release as installable only
when its APK has a valid Android signature and the signer matches the
repository's pinned production certificate.

## Android release integrity

**Do not install the legacy Android releases `android-v22` or `android-v24`.**
Their published assets are named `app-release-unsigned.apk` and are unsigned.
Both assets currently have SHA-256:

`c6fbf50f3cd34e52efed101054feb407c8fe772638826cfab53d4b754a976939`

A checksum can detect accidental corruption; it does not authenticate an
unsigned APK. These two GitHub Release assets have not been removed by this
notice and may remain visible. Treat them as withdrawn and untrusted.

The last audit-confirmed VpnHood production release is
[`vpnhood-android-v1`](https://github.com/GhostWebEnterprise/ghost-web-vpn/releases/tag/vpnhood-android-v1).
Its release APK must still be checked against the pinned production signer
before use. The expected production certificate SHA-256 is:

`5b389450352bfe408c0a7be6920f4510e09add61156306a747286125e638dcb9`

**Known checksum-sidecar limitation for `vpnhood-android-v1`:** the original
workflow generated the sidecar from the repository root, so it records the
relative path `release/GhostWeb-VPN-VpnHood-release.apk`. GitHub publishes the
APK asset under the basename `GhostWeb-VPN-VpnHood-release.apk`; therefore the
unmodified sidecar may not pass `sha256sum --check` when both downloaded
assets are placed in the same directory. The APK itself was verified in the
release job with SHA-256
`93b8cdf4f50d55c8cee4446ea83eb0da3ce6cff42b203785611fac002115ed9c`, matching
the GitHub APK asset digest, and with V2/V3 signature verification plus the
pinned production signer. For a local check, hash the downloaded APK directly
and compare it with that value. The current release workflow computes the
sidecar from inside the release directory so future assets use a portable
basename.

CI debug APKs are for build verification only. They are not production releases
and must never be substituted for a production-signed APK.

Future Android releases must pass all of the following before publication:

- Reject unsigned APKs and `*-unsigned-*` filenames.
- Verify with `apksigner verify --verbose --print-certs`.
- Require APK Signature Scheme V2 and exactly one signer.
- Match the pinned production certificate fingerprint.
- Verify the application ID, launcher identity and required VpnHood client
  libraries.
- Publish the APK and SHA-256 evidence from the same verified build.

## Reporting a vulnerability

Report security issues privately to
[support-ghostweb@proton.me](mailto:support-ghostweb@proton.me).

Include the affected release or commit, impact, and reproducible steps. Do not
include access keys, passwords, keystores or other secrets in a report.
