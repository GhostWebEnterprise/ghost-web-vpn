# Ghost Web VPN Android build

This directory contains the native system-wide VPN client.

The Android Actions workflow builds both debug and release APKs. A signed `app-release.apk` is produced when the repository signing secrets are configured; otherwise the workflow publishes the unsigned release APK artifact.

Release verification gate: CI must be green before this Android build is accepted.
