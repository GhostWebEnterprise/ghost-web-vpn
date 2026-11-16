# Legacy Android build directory

This directory is retained for legacy/reference purposes. It is **not** the authoritative VpnHood Android release path.

The supported GhostWeb VpnHood client is built from:

`vpnhood-android/GhostWeb.VpnHood.Android.csproj`

That project uses the pinned `VpnHood.Client` and `VpnHood.Client.Device.Android` packages. The compile gate verifies the restored assemblies, builds the Android client, and accepts only one debug-signed APK for its short-lived CI artifact. A debug artifact is not a production release.

## Production release policy

The only supported VpnHood Android production release path is `.github/workflows/vpnhood-release.yml`, manually dispatched from the `main` branch.

That workflow:

- requires `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, and `ANDROID_KEY_PASSWORD`;
- fails when any signing input is absent or invalid;
- requires exactly one signed APK and rejects unsigned outputs;
- verifies the APK with `apksigner`, including V2 signature, one signer, and the pinned existing release certificate;
- checks package and GhostWeb branding metadata and excludes legacy WireGuard native libraries;
- creates checksum and signer evidence, then downloads the APK, checksum manifest, NuGet package provenance report, and signer report and compares those files byte-for-byte before making the draft release public.

Pull-request and ordinary push runs do not receive production signing secrets and do not publish a production release.

**Never distribute an APK from this legacy directory or accept an unsigned APK as a fallback.** If the production signing or verification gate fails, no release is published.
