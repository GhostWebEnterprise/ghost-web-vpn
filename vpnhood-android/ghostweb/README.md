# GhostWeb Secure Server Pool

This directory defines the first production policy layer for GhostWeb VPN.

## Security rules

- Server access keys are never committed to Git.
- A region remains disabled until a real GhostWeb-controlled VpnHood SERVER is provisioned and its access key is stored securely.
- Smart Connect selects only healthy configured nodes and never falls back to an unprotected connection.
- Auto-Protect requires VPN connectivity for protected traffic, keeps Private DNS enabled, and reconnects after network changes.
- The existing `android-v30` release remains the rollback baseline.

## Initial regions

Sweden, Finland, Netherlands, Germany and United States. These are desired pool slots, not claims that servers already exist.

VpnHood SERVER must run on a controlled VPS and issue a `vh://` access key. Treat every access key as a secret.
