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
            "application-label:'GhostWeb VPN'\n"
            "application-debuggable\n"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing production release", result.stderr)

    def test_rejects_wrong_application_label(self):
        result = self.run_guard(
            "package: name='cfd.ghostbin.ghostwebvpn' versionCode='853'\n"
            "application-label:'cfd.ghostbin.ghostwebvpn'\n"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("application label", result.stderr)

    def test_rejects_empty_badging_output(self):
        result = self.run_guard("")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing or empty", result.stderr)

    def test_all_signed_release_workflows_apply_the_guard(self):
        legacy_workflow = (
            ROOT / ".github" / "workflows" / "vpnhood-android.yml"
        ).read_text(encoding="utf-8")
        legacy_release = legacy_workflow.split("  signed-release-build:", 1)[1]
        self.assertIn(
            "bash scripts/verify-vpnhood-release-badging.sh apk-badging.txt",
            legacy_release,
        )

        verified_workflow = (
            ROOT / ".github" / "workflows" / "vpnhood-release.yml"
        ).read_text(encoding="utf-8")
        verified_release = verified_workflow.split("  verified-release:", 1)[1]
        self.assertIn(
            "bash scripts/verify-vpnhood-release-badging.sh apk-badging.txt",
            verified_release,
        )

    def test_release_requires_nuget_provenance_report(self):
        verified_workflow = (
            ROOT / ".github" / "workflows" / "vpnhood-release.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("VPNHOOD-NUGET-PACKAGES.txt", verified_workflow)
        self.assertIn("cmp -s release/VPNHOOD-NUGET-PACKAGES.txt", verified_workflow)

    def test_verified_release_requires_compiled_vpnhood_android_assemblies(self):
        verified_workflow = (
            ROOT / ".github" / "workflows" / "vpnhood-release.yml"
        ).read_text(encoding="utf-8")
        verified_release = verified_workflow.split("  verified-release:", 1)[1]
        self.assertIn(
            "grep -Fq 'lib/arm64-v8a/lib_VpnHood.Client.dll.so' apk-contents.txt",
            verified_release,
        )
        self.assertIn(
            "grep -Fq 'lib/arm64-v8a/lib_VpnHood.Client.Device.Android.dll.so' apk-contents.txt",
            verified_release,
        )


if __name__ == "__main__":
    unittest.main()
