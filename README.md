<div align="center">

<img src="icon.svg" width="128" alt="GhostWeb VPN icon" />

# GhostWeb VPN

**Private by design. Secure by default. Open source.**

> **Development status:** GhostWeb VPN is under active development. The current codebase and development builds are not yet presented as production-ready privacy infrastructure.

Privacy-focused browser routing and VPN tooling for endpoints you control.

[![GitHub](https://img.shields.io/badge/GitHub-GhostWebEnterprise-181717?style=plastic&logo=github&logoColor=white)](https://github.com/GhostWebEnterprise)
[![Status](https://img.shields.io/badge/Status-Under%20Development-orange?style=plastic)](https://github.com/GhostWebEnterprise/ghost-web-vpn)
[![Platform](https://img.shields.io/badge/Platform-Browser%20%7C%20Android%20%7C%20Desktop-3DDC84?style=plastic&logo=android&logoColor=white)](https://github.com/GhostWebEnterprise/ghost-web-vpn)
[![Release](https://img.shields.io/github/v/release/GhostWebEnterprise/ghost-web-vpn?style=plastic&label=GhostWeb%20VPN)](https://github.com/GhostWebEnterprise/ghost-web-vpn/releases)
[![Test](https://img.shields.io/github/actions/workflow/status/GhostWebEnterprise/ghost-web-vpn/ci.yml?branch=main&style=plastic&label=Test)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/ci.yml)
[![Android](https://img.shields.io/github/actions/workflow/status/GhostWebEnterprise/ghost-web-vpn/android.yml?branch=main&style=plastic&label=Android)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/android.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/GhostWebEnterprise/ghost-web-vpn/codeql.yml?branch=main&style=plastic&label=CodeQL)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/codeql.yml)
[![Super-Linter](https://img.shields.io/github/actions/workflow/status/GhostWebEnterprise/ghost-web-vpn/super-linter.yml?branch=main&style=plastic&label=Super-Linter)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/super-linter.yml)
[![Website](https://img.shields.io/badge/Project%20Hub-ghostwebenterprise.github.io-0b57d0?style=plastic&logo=googlechrome&logoColor=white)](https://ghostwebenterprise.github.io/vpn.html)

</div>

---

## 👻 GhostWeb ecosystem

GhostWeb VPN is the network-privacy project in the GhostWeb ecosystem.

| Project | Purpose | Status |
|---|---|---|
| **GhostWeb Signal** | Privacy-focused Android messaging and calling | Public project |
| **GhostWeb VPN** | Browser, Android and desktop network protection | **Under development** |
| **GhostWeb AI** | AI client, agents and delivery tooling | Public project |
| **GhostOS** | Privacy-focused custom Android ROM | **In development** |

**Project hub:** https://ghostwebenterprise.github.io/

## 🚧 Current status

GhostWeb VPN is being actively developed and verified. Architecture, clients, privacy behavior, CI and packaging may change before a stable release.

Do not rely on a development build as your only privacy or security control. A release appearing in GitHub does not by itself mean the project has reached production-ready status; stable status will be stated explicitly when the relevant functionality has been validated.

### Development focus

- Clear connection and disconnection state
- Fail-closed / kill-switch behavior
- Endpoint, public-IP and region verification
- Browser leak hardening, including WebRTC-related controls
- Android system-wide VPN integration
- Desktop client and packaging
- User-controlled or explicitly configured endpoints
- CI, security scanning and reproducible release workflows

## 🌐 Architecture and clients

The repository contains work toward multiple GhostWeb VPN surfaces:

- **Browser:** Chromium/Manifest V3 routing and privacy controls.
- **Android:** native system-wide VPN work using Android VPN APIs and tunnel components.
- **Desktop:** cross-platform client and packaging work.

The intended model favors endpoints that users explicitly configure or control rather than silently depending on an unspecified bundled network.

## 🛡️ Privacy & security

Security-sensitive behavior must be treated as unverified until it has passed the relevant implementation, build and runtime gates. In particular, kill-switch behavior, leak prevention, routing correctness and endpoint verification require real-world validation before a stable release claim.

Never expose unauthenticated proxy listeners publicly. Verify your endpoint configuration and network behavior independently when testing development builds.

## 📱 Android development

```sh
cd android
gradle assembleDebug
gradle assembleRelease
```

Successful compilation is one development gate; it is not equivalent to verification of network/privacy behavior.

## 🖥️ Desktop development

```sh
cd desktop
npm install
npm run dist
```

## 📦 Browser development

For local development, clone the repository, load the unpacked extension in a Chromium-based browser, configure an endpoint you control, and independently verify routing and leak behavior.

## 🧪 Verification & CI

The project uses CI for source checks, linting, security analysis, packaging and Android builds. Development continues through the gate sequence **build → test → first real failure → fix → rebuild → verify**.

Before GhostWeb VPN is marked stable, the project should verify at minimum build integrity, connection lifecycle, routing behavior, fail-closed behavior, DNS/WebRTC leak handling where applicable, endpoint/IP verification and release artifacts.

## 🤝 Contributing

Issues, improvements, security reports, documentation updates and pull requests are welcome.

- [Issues](https://github.com/GhostWebEnterprise/ghost-web-vpn/issues)
- [Pull requests](https://github.com/GhostWebEnterprise/ghost-web-vpn/pulls)
- [Releases](https://github.com/GhostWebEnterprise/ghost-web-vpn/releases)
- [GhostWeb VPN development page](https://ghostwebenterprise.github.io/vpn.html)

## 📬 Contact

Questions, feedback or support requests: **ghostweb@ghostbin.cfd**

---

<div align="center">

**GhostWeb VPN** · network privacy under active development 👻

</div>
