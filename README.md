<div align="center">

<img src="icon.svg" width="96" height="96" alt="Ghost Web VPN logo">

# Ghost Web VPN by Ghost Web Enterprise ©

**Private browser routing. Ghost-style protection. Your endpoint, your traffic path.**

A privacy-focused Chromium proxy client built from scratch as a Manifest V3 extension. Route browser traffic through an endpoint you control, verify the route live, and reduce browser-level location leakage.

[![CI](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/ci.yml?query=branch%3Amain)
[![Manifest V3](https://img.shields.io/badge/Chrome-Manifest%20V3-67e8a2?logo=googlechrome&logoColor=white)](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-manifest-v3)
[![Self-hosted](https://img.shields.io/badge/Endpoint-Self--Hosted-67e8a2)](server/free-self-hosted/README.md)
[![FOSSVPS](https://img.shields.io/badge/Cloud-FOSSVPS-67e8a2)](https://fossvps.org/)

</div>

---

## 👻 Ghost Web: Virtual Private Network

Ghost Web VPN follows one principle: **the browser should use an endpoint you control, not a bundled third-party proxy fleet.**

The extension configures Chromium's proxy stack, checks whether the route actually works, remembers the last endpoint, and restores it after browser restarts.

> **Important:** Ghost Web VPN is a **browser proxy client**, not a standalone network-level VPN. A system-wide VPN requires a separately operated gateway such as WireGuard or OpenVPN.

## ✨ What it does

| Area | Ghost Web VPN |
| --- | --- |
| 🔌 Connection | One-click connect / disconnect |
| ✅ Verification | Live connectivity check through the proxy |
| 🔁 Recovery | Auto-reconnect and keep-alive |
| 🌍 Location | Region presets + connection-based detection |
| 🕒 Browser privacy | Geolocation, timezone, `Date`, `Intl` and permission surfaces |
| 🌐 Protocols | HTTP, HTTPS, SOCKS4 and SOCKS5 |
| 🔐 HTTP(S) auth | `onAuthRequired` authentication |
| 💾 Storage | Persistent local extension configuration |
| 🧩 Platform | Chromium / Chrome Manifest V3 |
| 🖥️ Endpoint | Self-hosted and user-controlled |
| 🚫 Bundled servers | None |

## 🚀 Quick Start

### Option 0 — Android app (real VPN, system-wide)

The repository ships a native Android VPN client (`android/`) built on the official
[WireGuard Android tunnel library](https://github.com/WireGuard/wireguard-android)
(`VpnService` + wireguard-go). It connects to the same Ghost endpoint stack
(`server/docker-compose.yml`) and routes **all device traffic**, not just browser traffic.

**Get the APK:** every push to the Android project builds a debug APK plus a release APK via GitHub Actions. Download the `ghost-web-vpn-android` (debug) or `ghost-web-vpn-android-release` (signed release) artifact from the [Android workflow](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/android.yml). Without signing secrets configured, the release artifact is `ghost-web-vpn-android-release-unsigned`.

**Build locally:**

```sh
cd android
gradle assembleDebug   # APK at app/build/outputs/apk/debug/app-debug.apk
gradle assembleRelease # release APK at app/build/outputs/apk/release/
```

**Release signing (one-time setup):** the release APK is signed from GitHub
secrets, so the artifact installs directly on a device.

1. Generate a keystore (keep it and its passwords private — never commit it):

```sh
keytool -genkeypair -v -keystore ghost-release.keystore \
  -alias ghost -keyalg RSA -keysize 2048 -validity 10000
```

2. Add these repository secrets (**Settings → Secrets and variables → Actions**):

| Secret | Value |
| --- | --- |
| `ANDROID_KEYSTORE_BASE64` | `base64 -w0 ghost-release.keystore` output |
| `ANDROID_KEYSTORE_PASSWORD` | keystore password |
| `ANDROID_KEY_ALIAS` | e.g. `ghost` |
| `ANDROID_KEY_PASSWORD` | key password (defaults to the keystore password if unset) |

3. Push (or re-run the workflow) — the release artifact is then `app-release.apk`, signed and installable.

For local release builds, put the same values in `android/keystore.properties`
(git-ignored): `storeFile`, `storePassword`, `keyAlias`, `keyPassword`.

**Connect:** install the APK → paste the WireGuard peer config printed by your Ghost
endpoint (or fill in the fields: private key, address, server public key,
`SERVERURL:SERVERPORT`, allowed IPs) → press **Connect** → approve the Android VPN
consent dialog. A quick-settings tile and reboot auto-reconnect are included.

### Option A — Free self-hosted endpoint

Use a Linux machine you already control: home PC, mini-PC, Raspberry Pi, or always-on server. The included setup uses Tailscale's free tier and a SOCKS5 proxy bound to the private Tailscale address.

```sh
cd server/free-self-hosted
sudo bash setup-free-endpoint.sh
```

The installer prints the settings to enter in Ghost Web VPN:

```text
Protocol: socks5
Host:     100.x.y.z
Port:     1080
Username: blank
Password: blank
```

Press **Connect**. Ghost verifies the route instead of assuming that the proxy configuration succeeded.

→ **[Full free-endpoint guide](server/free-self-hosted/README.md)**

### Option B — Free VPS / FOSSVPS

The repository also contains deployment tooling for free open-source VPS infrastructure. **FOSSVPS is the primary free VPS target** for the project; the intended deployment flow is SSH details → bootstrap → configured endpoint.

→ **[FOSSVPS](https://fossvps.org/)**  
→ **[Server deployment](server/README.md)**

## 🧭 Architecture

```text
┌───────────────────────┐
│  Chromium + Ghost     │
│  Web VPN Extension    │
└───────────┬───────────┘
            │ chrome.proxy
            ▼
┌───────────────────────┐
│ Your proxy endpoint   │
│ SOCKS4 / SOCKS5 /     │
│ HTTP / HTTPS          │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Endpoint Internet     │
│ connection / public IP│
└───────────────────────┘
```

## 🛡️ Browser protection

A proxy changes the network path, but browsers can expose additional location signals. Ghost includes a `document_start` content script for browser-level location protection.

It can align:

- Geolocation API results
- Browser timezone
- `Date` timezone behaviour
- `Intl` locale/timezone surfaces
- Relevant permission responses
- Best-effort WebRTC hardening while connected

Choose a region preset or detect a region from the active connection.

## 🔐 SOCKS5 security note

Chrome does not provide SOCKS5 proxy authentication through the extension proxy API, so SOCKS4/SOCKS5 credentials remain blank.

For the included free endpoint, the proxy is bound to the machine's **Tailscale address**, not a public interface. **Do not expose an unauthenticated SOCKS5 listener on `0.0.0.0`.**

HTTP(S) authentication remains supported through `onAuthRequired`, with credentials kept in extension storage rather than source control.

## 📦 Install the extension

1. Clone this repository.
2. Open `chrome://extensions` in Chrome or Chromium.
3. Enable **Developer mode**.
4. Select **Load unpacked**.
5. Choose the repository directory.
6. Enter the protocol, host and port for an endpoint you control.
7. Press **Connect**.
8. Confirm the live connectivity check reports success.

GitHub Actions packages the extension as `ghost-web-vpn.zip`.

## 🧪 Verification & CI

Every push to `main` and every pull request runs the validation workflow. The CI gate checks:

- Manifest JSON validity
- JavaScript syntax for all extension scripts
- Required extension/server files
- Manifest V3 permissions and structure
- Docker Compose configuration
- Setup-script shell hygiene when ShellCheck is available
- Private-key material accidentally committed
- Creation of the distributable extension ZIP

**Build gate:** `validate` → package → artifact upload.

[![CI](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/GhostWebEnterprise/ghost-web-vpn/actions/workflows/ci.yml?query=branch%3Amain)

## 📁 Project structure

```text
ghost-web-vpn/
├── android/                      # Native Android VPN client (WireGuard tunnel)
│   ├── app/                      # Kotlin app: import, connect, stats, QS tile
│   ├── scripts/                  # Launcher icon generator
│   └── settings.gradle.kts       # Gradle project definition
├── background.js                 # Proxy lifecycle, reconnect and auth
├── popup.html                    # Extension UI
├── popup.css                     # Ghost dark UI styling
├── popup.js                      # Controls and connectivity checks
├── presets.js                    # Region presets
├── spoof.js                      # Browser location/privacy layer
├── manifest.json                 # Chrome Manifest V3 definition
├── icon.svg                      # Ghost brand icon
├── icons/                        # Extension PNG icons
├── QUICKSTART.md                 # From-zero setup guide
├── server/
│   ├── README.md                 # Server/deployment documentation
│   ├── docker-compose.yml        # Endpoint stack
│   └── free-self-hosted/         # Tailscale endpoint
└── .github/workflows/
    ├── ci.yml                    # Extension validation + ZIP packaging
    └── android.yml               # Android APK build + artifact upload
```

## 🧱 Design principles

### Privacy first
Ghost does not bundle a commercial proxy network. You choose and operate the endpoint.

### Fail visibly
Connection state is verified instead of assuming that applying a Chromium proxy configuration means traffic is working.

### Keep credentials out of Git
Private keys, passwords and long-lived secrets belong in authenticated configuration or secret storage — never source control.

### Minimal surface
The extension stays focused on browser routing, verification and browser-level privacy controls.

## ⚠️ Limitations

- Not a system-wide VPN by itself.
- The endpoint must be online.
- Destination websites see the endpoint's public IP.
- Home/self-hosted performance depends on upload bandwidth and ISP.
- SOCKS5 authentication is unavailable through Chromium's extension API.
- Location spoofing reduces browser-level leakage but cannot guarantee anonymity against every fingerprinting technique.

## 🗺️ Roadmap

- [x] Manifest V3 Chromium extension
- [x] HTTP / HTTPS / SOCKS4 / SOCKS5
- [x] Live connection verification
- [x] Persistent endpoint configuration
- [x] Auto-reconnect / keep-alive
- [x] Region presets and connection detection
- [x] Browser location protection
- [x] Free Tailscale self-hosted endpoint
- [x] Automated CI validation and ZIP packaging
- [x] FOSSVPS deployment target
- [x] Native Android system-wide VPN client
- [ ] Hardened production provisioning
- [ ] Expanded endpoint health diagnostics
- [ ] Additional Chromium privacy hardening

## 📚 Documentation

- **[Quick Start](QUICKSTART.md)** — from clone to working endpoint
- **[Free self-hosted endpoint](server/free-self-hosted/README.md)** — Tailscale + SOCKS5
- **[Server documentation](server/README.md)** — endpoint and deployment options
- **[CI workflow](.github/workflows/ci.yml)** — validation and packaging
- **[Android workflow](.github/workflows/android.yml)** — APK build and release artifact

## 🤝 Contributing

Issues, improvements and pull requests are welcome. Keep changes privacy-focused, avoid hard-coded credentials, and keep CI green.

## 📬 Contact

Questions, feedback or support requests: **ghostweb@ghostbin.cfd**

---

<div align="center">

**Ghost Web VPN** · private routing for the browser you control 👻

</div>
