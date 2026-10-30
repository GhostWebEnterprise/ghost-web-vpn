import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "vpnhood-android"


class VpnHoodActivityLifecycleTests(unittest.TestCase):
    def test_client_session_is_app_scoped_and_serializes_transitions(self):
        session = (ANDROID / "VpnHoodClientSession.cs").read_text(encoding="utf-8")
        self.assertIn("private static VpnHoodClient? _client", session)
        self.assertIn("Lazy<AndroidDevice>", session)
        self.assertIn("SemaphoreSlim OperationLock", session)
        self.assertIn("public static bool ClearClient(VpnHoodClient client)", session)

        activity = (ANDROID / "MainActivity.cs").read_text(encoding="utf-8")
        self.assertIn("await VpnHoodClientSession.OperationLock.WaitAsync()", activity)
        self.assertIn("VpnHoodClientSession.OperationLock.Release()", activity)
        self.assertIn("AttachExistingClient()", activity)
        self.assertIn("VpnHoodClientSession.SetClient(client)", activity)

    def test_activity_destroy_detaches_observer_without_disposing_tunnel(self):
        activity = (ANDROID / "MainActivity.cs").read_text(encoding="utf-8")
        match = re.search(
            r"protected override void OnDestroy\(\)\s*\{(?P<body>.*?)\n    \}",
            activity,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "OnDestroy override must remain explicit")
        body = match.group("body")
        self.assertIn("StateChanged -= OnClientStateChanged", body)
        self.assertNotIn("DisposeAsync", body)
        self.assertNotIn("TryDisposeClientAsync", body)

    def test_failed_cleanup_keeps_client_available_for_retry(self):
        activity = (ANDROID / "MainActivity.cs").read_text(encoding="utf-8")
        self.assertRegex(
            activity,
            r"if \(await TryDisposeClientAsync\(connectedClient\)\).*?"
            r"ClearClient\(connectedClient\).*?else\s*\{.*?"
            r"Disconnect failed; VPN state is unknown",
        )
        self.assertIn("Connection failed and cleanup failed; VPN state is unknown", activity)


if __name__ == "__main__":
    unittest.main()
