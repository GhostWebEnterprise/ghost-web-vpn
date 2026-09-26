# GhostWeb VPN — VpnHood Android migration

This branch migrates the Android VPN engine from WireGuard to VpnHood.

The migration uses the official VpnHood NuGet packages `VpnHood.Client` and
`VpnHood.Client.Device.Android`. VpnHood is licensed under LGPL-2.1-only.
See the upstream project and license before redistribution:
https://github.com/vpnhood/VpnHood

The existing android-v30 release remains the rollback baseline.
