# GhostWeb VPN — VpnHood Android migration

Status: active migration branch. `android-v30` / commit `b2b9ace0` remains the rollback baseline and must not be rewritten.

## Upstream

Engine source: https://github.com/vpnhood/VpnHood (`develop`). VpnHood is LGPL-2.1-only. Preserve upstream copyright/license notices and provide corresponding source/notice access for redistributed VpnHood components.

Verified upstream Android head: `src/Apps/Client/Client.Android.Web/VpnHood.App.Client.Android.Web.csproj`, currently targeting `net10.0-android36.1` with Android API 24 minimum and arm64/x64/arm release RIDs. The app is built on VpnHood AppLib plus Avalonia Android UI hosting.

## Migration gates

1. Vendor/fork the required VpnHood source into a source-built Android module; do not ship the old WireGuard engine in the migrated APK.
2. Apply GhostWeb package ID, product name, icons, company/domain links, privacy/terms links and update metadata without removing LGPL notices.
3. Preserve VpnHood access-key import (`vh`, `vhkey`, supported MIME types) and expose GhostWeb access-key configuration.
4. Wire Android VPN permission and connect/disconnect through VpnHood's Android device/app layer.
5. Expose kill switch, split tunneling and private DNS only through capabilities actually supported by the selected upstream revision; do not emulate unsupported security guarantees.
6. Add .NET 10 Android workload/build CI alongside the existing v30 rollback build until migration validation is complete.
7. Use the existing GhostWeb Android signing identity. Never commit keystore material or secret values.
8. Verify release APK signature, SHA-256 and absence of legacy WireGuard native libraries before publication.
9. Publish a new GitHub Release only after the migrated APK passes build/signature checks. Keep `android-v30` available as rollback.

## Release acceptance

A migration release is complete only when CI evidence proves: VpnHood source build succeeds; signed APK exists; `apksigner verify` succeeds; SHA-256 is recorded; legacy `libwg-go.so`, `libwg-quick.so` and `libwg.so` are absent; and the exact APK is attached to a public GitHub Release.
