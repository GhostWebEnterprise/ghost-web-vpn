import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "verify-vpnhood-release-badging.sh"


class VpnHoodReleaseBadgingGuardTests(unittest.TestCase):
    def run_guard(self, output: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            badging = Path(directory) / "apk-badging.txt"
            badging.write_text(output, encoding="utf-8")
            return subprocess.run(
                ["bash", str(GUARD), str(badging)],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_accepts_non_debuggable_release_apk(self):
        result = self.run_guard(
            "package: name='cfd.ghostbin.ghostwebvpn' versionCode='853'\n"
            "application-label:'GhostWeb VPN'\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not debuggable", result.stdout)

    def test_rejects_debuggable_apk(self):
        result = self.run_guard(
            "package: name='cfd.ghostbin.ghostwebvpn' versionCode='853'\n"
            "application-debuggable\n"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing production release", result.stderr)

    def test_rejects_empty_badging_output(self):
        result = self.run_guard("")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing or empty", result.stderr)


if __name__ == "__main__":
    unittest.main()
