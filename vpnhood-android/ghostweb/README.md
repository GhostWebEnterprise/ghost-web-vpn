# GhostWeb Secure Server Pool

This pull request introduces a **proposed policy schema and validation gate** for a future GhostWeb-controlled VpnHood server pool. It is not yet wired into the Android client and must not be treated as an active protection feature.

## Current implementation boundary

- The current Android client still asks the user to enter a VpnHood access key manually.
- The client does not yet consume `server-pool.json` or `protection-policy.json`.
- Smart Connect health checks, lowest-latency node selection, automatic reconnection policy, and Auto-Protect enforcement are not implemented by these JSON files.
- No GhostWeb-controlled production VpnHood nodes or access keys are provisioned by this change.
- All initial region slots remain disabled until a real server is provisioned, independently tested, and its access key is delivered through a secure device-side provisioning flow.

## Security rules for the future integration

- Never commit VpnHood access keys to Git.
- Keep protected traffic fail-closed; never fall back to an unprotected route.
- Store provisioned access keys in Android-backed secure storage, not in repository configuration.
- Validate server health and policy state before enabling a region.
- Keep the existing `vpnhood-android-v1` release as the production rollback baseline until a replacement has passed the full release gate.

## Initial region slots

Sweden, Finland, Netherlands, Germany and United States are planned slots only. Their presence in the schema is not evidence that servers exist or are reachable.

VpnHood SERVER must run on a controlled VPS and issue a `vh://` access key. Treat every access key as a secret.
