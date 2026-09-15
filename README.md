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
[![Website](https://img.shields.io/badge/Website-GhostWeb-0b57d0?style=plastic&logo=googlechrome&logoColor=white)](https://ghostwebenterprise.github.io/ghostweb.signal/)

</div>

---

## 👻 GhostWeb ecosystem

**GhostWeb VPN** is part of the GhostWeb open-source ecosystem for privacy, secure communication, network protection, and AI tooling.

| Project | Purpose | Status |
|---|---|---|
| **GhostWeb Signal** | Privacy-focused Android messaging and calling | **Available** |
| **GhostWeb VPN** | Browser and network protection | **Available** |
| **GhostWeb AI** | AI client, agents, and delivery tooling | **Available** |

**Project hub:** https://ghostwebenterprise.github.io/ghostweb.signal/

---

## 🌐 What GhostWeb VPN does

GhostWeb VPN is a **browser proxy client plus a native Android VPN client**. The Chromium extension routes browser traffic through an endpoint you control, while the Android application can provide system-wide WireGuard-based VPN routing.

> The Chromium extension is not a standalone system-wide VPN. For device-wide routing, use the included Android client or operate a separate WireGuard/OpenVPN gateway.

### Highlights

- One-click connect / disconnect
- Live proxy connectivity verification
- HTTP, HTTPS, SOCKS4 and SOCKS5 support
- Region presets and connection-based detection
- Browser geolocation and timezone protection
- Best-effort WebRTC hardening
- Persistent endpoint configuration and reconnect support
- Self-hosted endpoint support
- Free endpoint tooling and FOSSVPS deployment target
- Native Android system-wide VPN client using WireGuard
- No bundled commercial proxy fleet

## 🛡️ Privacy & security

GhostWeb VPN follows a simple principle: **use an endpoint you control rather than silently routing traffic through a bundled third-party network.**

The extension verifies that the configured route actually works instead of treating a successful proxy configuration as proof of connectivity.

Browser privacy controls can align:

- Geolocation API results
- Browser timezone
- `Date` timezone behaviour
- `Intl` locale/timezone surfaces
- Relevant permission responses
- Best-effort WebRTC behaviour while connected

Do not expose an unauthenticated SOCKS5 listener on `0.0.0.0`.

## 📱 Android VPN

The `android/` application uses Android `VpnService` and the WireGuard tunnel library to route device traffic through the same Ghost endpoint stack.

**Build locally:**

```sh
cd android
gradle assembleDebug
gradle assembleRelease
```

Release APK artifacts are produced by GitHub Actions. If release signing secrets are not configured, the release artifact is unsigned.

## 🌍 Endpoint options

### Self-hosted

The repository includes a free self-hosted endpoint setup using a Linux machine and Tailscale.

```sh
cd server/free-self-hosted
sudo bash setup-free-endpoint.sh
```

### FOSSVPS

FOSSVPS is the project's primary free VPS deployment target. The intended flow is SSH information → bootstrap → configured endpoint.

- https://fossvps.org/
- [Server deployment](server/README.md)

## 📦 Install the Chromium extension

1. Clone this repository.
2. Open `chrome://extensions` in Chrome or Chromium.
3. Enable **Developer mode**.
4. Select **Load unpacked**.
5. Choose the repository directory.
6. Enter an endpoint you control.
7. Press **Connect**.
8. Confirm the live connectivity check succeeds.

GitHub Actions packages the extension as `ghost-web-vpn.zip`.

## 🧪 Verification & CI

Every push to `main` and every pull request runs the validation, security and lint workflows. The project verifies:

- Manifest JSON validity
- JavaScript syntax
- Required extension and server files
- Manifest V3 structure and permissions
- Docker Compose configuration
- Shell setup hygiene when ShellCheck is available
- Accidental private-key material
- Creation of the distributable extension ZIP
- JavaScript/TypeScript, JSON, YAML, Markdown, Bash and GitHub Actions linting
- CodeQL security analysis
- Automated dependency-update configuration through Dependabot

The Android workflow separately builds the native VPN application and publishes APK artifacts.

**Delivery gate:** `validate → lint → security → package → artifact → verify`.

## 🏗️ Architecture

```text
┌─────────────────────────┐
│ Chromium / GhostWeb VPN │
│ Manifest V3 extension   │
└────────────┬────────────┘
             │ chrome.proxy
             ▼
┌─────────────────────────┐
│ Your endpoint           │
│ HTTP / HTTPS / SOCKS    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Internet / public IP    │
└─────────────────────────┘
```

Android adds a native `VpnService` + WireGuard tunnel for system-wide traffic.

## 📁 Project structure

```text
ghost-web-vpn/
├── android/                    # Native Android VPN client
├── background.js               # Proxy lifecycle and authentication
├── popup.html                  # Extension UI
├── popup.js                    # Controls and connectivity checks
├── popup.css                   # Ghost UI styling
├── presets.js                  # Region presets
├── spoof.js                    # Browser privacy layer
├── manifest.json               # Chromium Manifest V3
├── icon.svg                    # GhostWeb icon
├── server/                     # Endpoint and deployment tooling
│   ├── README.md
│   ├── docker-compose.yml
│   └── free-self-hosted/
├── QUICKSTART.md
└── .github/
    ├── dependabot.yml
    └── workflows/
        ├── ci.yml
        ├── android.yml
        ├── codeql.yml
        └── super-linter.yml
```

## ⚠️ Limitations

- The browser extension is not a system-wide VPN.
- Endpoint availability and bandwidth determine performance.
- Destination sites see the endpoint's public IP.
- SOCKS5 authentication is unavailable through Chromium's extension proxy API.
- Browser privacy hardening cannot guarantee anonymity against every fingerprinting technique.

## 🗺️ Roadmap

- [x] Manifest V3 Chromium extension
- [x] HTTP / HTTPS / SOCKS4 / SOCKS5
- [x] Live connection verification
- [x] Persistent endpoint configuration
- [x] Region presets and connection detection
- [x] Browser location protection
- [x] Free self-hosted endpoint
- [x] Automated CI validation and ZIP packaging
- [x] FOSSVPS deployment target
- [x] Native Android system-wide VPN client
- [x] CodeQL security workflow
- [x] Super-Linter workflow
- [x] Dependabot configuration
- [ ] Hardened production provisioning
- [ ] Expanded endpoint health diagnostics
- [ ] Additional Chromium privacy hardening

## 🤝 Contributing

Issues, improvements, security reports, documentation updates, and pull requests are welcome. Keep changes privacy-focused, avoid hard-coded credentials, and keep CI green.

- [Issues](https://github.com/GhostWebEnterprise/ghost-web-vpn/issues)
- [Pull requests](https://github.com/GhostWebEnterprise/ghost-web-vpn/pulls)
- [Releases](https://github.com/GhostWebEnterprise/ghost-web-vpn/releases)

## 📬 Contact

Questions, feedback or support requests: **ghostweb@ghostbin.cfd**

---

<div align="center">

**GhostWeb VPN** · private routing for the browser and devices you control 👻

</div>
