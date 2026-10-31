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
        self.assertIn("InputType = Android.Text.InputTypes.ClassText | Android.Text.InputTypes.TextVariationPassword", activity)

    def test_activity_destroy_detaches_observer_without_disposing_tunnel(self):
        activity = (ANDROID / "MainActivity.cs").read_text(encoding="utf-8")
        on_destroy = activity.split("protected override void OnDestroy()", 1)[1]
        self.assertIn("StateChanged -= OnClientStateChanged", on_destroy)
        self.assertNotIn("DisposeAsync", on_destroy)
        self.assertNotIn("TryDisposeClientAsync", on_destroy)

    def test_failed_cleanup_keeps_client_available_for_retry(self):
        activity = (ANDROID / "MainActivity.cs").read_text(encoding="utf-8")
        disconnect = activity.split("var connectedClient = VpnHoodClientSession.Client", 1)[1]
        disconnect = disconnect.split("var accessKey =", 1)[0]
        self.assertIn("if (await TryDisposeClientAsync(connectedClient))", disconnect)
        self.assertIn("VpnHoodClientSession.ClearClient(connectedClient)", disconnect)
        self.assertIn("Disconnect failed; VPN state is unknown", disconnect)
        self.assertIn("Connection failed and cleanup failed; VPN state is unknown", activity)


if __name__ == "__main__":
    unittest.main()
