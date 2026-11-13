import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "verify-vpnhood-version-monotonic.py"
EXPECTED_PACKAGE = "cfd.ghostbin.ghostwebvpn"


class VpnHoodVersionMonotonicTests(unittest.TestCase):
    def run_guard(self, previous: str, candidate: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            previous_path = Path(directory) / "previous.txt"
            candidate_path = Path(directory) / "candidate.txt"
            previous_path.write_text(previous, encoding="utf-8")
            candidate_path.write_text(candidate, encoding="utf-8")
            return subprocess.run(
                ["python3", str(GUARD), str(previous_path), str(candidate_path)],
                check=False,
                capture_output=True,
                text=True,
            )

    def badging(self, code: int) -> str:
        return (
            f"package: name='{EXPECTED_PACKAGE}' versionCode='{code}' "
            f"versionName='8.2.{code}' platformBuildVersionCode='36'\n"
        )

    def test_accepts_strictly_newer_version_code(self):
        result = self.run_guard(self.badging(853), self.badging(854))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("advances from 853 to 854", result.stdout)

    def test_rejects_same_version_code(self):
        result = self.run_guard(self.badging(853), self.badging(853))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("candidate 853 <= published 853", result.stderr)

    def test_rejects_downgrade_from_published_release(self):
        result = self.run_guard(self.badging(853), self.badging(610))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("candidate 610 <= published 853", result.stderr)

    def test_rejects_wrong_package_identity(self):
        candidate = "package: name='com.vpnhood.client.android.web' versionCode='854'\n"
        result = self.run_guard(self.badging(853), candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected application ID", result.stderr)

    def test_rejects_missing_version_code(self):
        candidate = f"package: name='{EXPECTED_PACKAGE}' versionName='8.2.854'\n"
        result = self.run_guard(self.badging(853), candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no numeric versionCode", result.stderr)

    def test_signed_source_build_uses_canonical_ghostweb_version(self):
        workflow = (
            ROOT / ".github" / "workflows" / "vpnhood-android.yml"
        ).read_text(encoding="utf-8")
        release_job = workflow.split("  signed-release-build:", 1)[1]
        self.assertIn("Read canonical GhostWeb Android version", release_job)
        self.assertIn('-p:ApplicationVersion="$GHOSTWEB_APP_VERSION_CODE"', release_job)
        self.assertIn('-p:ApplicationDisplayVersion="$GHOSTWEB_APP_VERSION_NAME"', release_job)
        self.assertIn("verify-vpnhood-version-monotonic.py", release_job)

    def test_both_signed_release_paths_compare_with_latest_published_apk(self):
        for workflow_name, job_marker in (
            ("vpnhood-android.yml", "  signed-release-build:"),
            ("vpnhood-release.yml", "  verified-release:"),
        ):
            workflow = (
                ROOT / ".github" / "workflows" / workflow_name
            ).read_text(encoding="utf-8")
            release_job = workflow.split(job_marker, 1)[1]
            self.assertIn('gh release download "$LATEST_VPNHOOD_TAG"', release_job)
            self.assertIn("verify-vpnhood-version-monotonic.py", release_job)


if __name__ == "__main__":
    unittest.main()
