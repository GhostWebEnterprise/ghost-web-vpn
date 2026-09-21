<div align="center">

<img src="icon.svg" width="128" alt="GhostWeb VPN icon" />

# GhostWeb VPN

**Private by design. Secure by default. Open source.**

Privacy-focused browser routing and VPN tooling for endpoints you control.

[![GitHub](https://img.shields.io/badge/GitHub-GhostWebEnterprise-181717?style=plastic&logo=github&logoColor=white)](https://github.com/GhostWebEnterprise)
[![Platform](https://img.shields.io/badge/Platform-Chromium%20%7C%20Android-3DDC84?style=plastic&logo=android&logoColor=white)](https://github.com/GhostWebEnterprise/ghost-web-vpn)
[![Release](https://img.shields.io/github/v/release/GhostWebEnterprise/ghost-web-vpn?style=plastic&label=GhostWeb%20VPN)](https://github.com/GhostWebEnterprise/ghost-web-vpn/releases)
[![License](https://img.shields.io/badge/License-Open%20Source-blue?style=plastic)](https://github.com/GhostWebEnterprise/ghost-web-vpn)
[![Test](https://img.shields.io/github/actions/workflow/status/GhostWebEnterprise/ghost-web-vpn/ci.yml?branch=main&style=plastic&label=Test)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/ci.yml)
[![Android](https://img.shields.io/github/actions/workflow/status/GhostWebEnterprise/ghost-web-vpn/android.yml?branch=main&style=plastic&label=Android)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/android.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/GhostWebEnterprise/ghost-web-vpn/codeql.yml?branch=main&style=plastic&label=CodeQL)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/codeql.yml)
[![Super-Linter](https://img.shields.io/github/actions/workflow/status/GhostWebEnterprise/ghost-web-vpn/super-linter.yml?branch=main&style=plastic&label=Super-Linter)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/super-linter.yml)
[![Dependabot](https://img.shields.io/github/issues/GhostWebEnterprise/ghost-web-vpn/dependabot?style=plastic&label=Dependabot)](https://github.com/GhostWebEnterprise/ghost-web-vpn/network/updates)
[![Website](https://img.shields.io/badge/Website-ghostweb.bot.cd-0b57d0?style=plastic&logo=googlechrome&logoColor=white)](https://ghostweb.bot.cd)

</div>

---

## 👻 GhostWeb ecosystem

**GhostWeb VPN** is part of the GhostWeb open-source ecosystem for privacy, secure communication, network protection, AI tooling, and privacy-focused Android development.

| Project | Purpose | Status |
|---|---|---|
| **GhostWeb Signal** | Privacy-focused Android messaging and calling | **Available** |
| **GhostWeb VPN** | Browser and network protection | **Available** |
| **GhostWeb AI** | AI client, agents, and delivery tooling | **Available** |
| **GhostOS** | Privacy-focused custom Android ROM | **In development** |

**Official project hub:** https://ghostweb.bot.cd

## 🌐 What GhostWeb VPN does

GhostWeb VPN provides a Chromium Manifest V3 proxy client, a native Android VPN client, and cross-platform desktop tooling for endpoints you control.

### Highlights

- One-click connect / disconnect
- HTTP, HTTPS, SOCKS4 and SOCKS5 endpoint support
- Live connectivity verification
- Browser geolocation and timezone protection
- Best-effort WebRTC hardening
- Persistent endpoint configuration
- Self-hosted endpoint support
- Native Android system-wide VPN client using WireGuard
- Desktop Electron application

## 🛡️ Privacy & security

GhostWeb VPN is designed around endpoints you control rather than silently routing traffic through a bundled third-party network. Do not expose unauthenticated proxy listeners publicly, and verify endpoint configuration before relying on it for sensitive traffic.

## 📱 Android VPN

The Android application uses Android `VpnService` and the WireGuard tunnel library.

```sh
cd android
gradle assembleDebug
gradle assembleRelease
```

## 🖥️ Desktop

The `desktop/` application supports Windows, macOS, and Linux packaging.

```sh
cd desktop
npm install
npm run dist
```

## 📦 Chromium extension

Clone the repository, open `chrome://extensions`, enable Developer mode, select Load unpacked, choose the repository directory, configure an endpoint you control, and verify connectivity.

## 🧪 Verification & CI

CI validates source, security, lint, packaging, Android builds, CodeQL, and dependency updates. Release APK artifacts are produced by GitHub Actions when the Android build succeeds.

## 🤝 Contributing

Issues, improvements, security reports, documentation updates, and pull requests are welcome.

- [Issues](https://github.com/GhostWebEnterprise/ghost-web-vpn/issues)
- [Pull requests](https://github.com/GhostWebEnterprise/ghost-web-vpn/pulls)
- [Releases](https://github.com/GhostWebEnterprise/ghost-web-vpn/releases)
- [GhostWeb project hub](https://ghostweb.bot.cd)

## 📬 Contact

Questions, feedback or support requests: **ghostweb@ghostbin.cfd**

---

<div align="center">

**GhostWeb VPN** · private routing for the browser and devices you control 👻

</div>
