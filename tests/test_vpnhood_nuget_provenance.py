import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORDER = ROOT / "scripts" / "record-vpnhood-nuget-provenance.py"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "vpnhood-release.yml"
CLIENT_WORKFLOW = ROOT / ".github" / "workflows" / "vpnhood-client-ci.yml"

PACKAGES = {
    "VpnHood.Client": "5.0.616-prerelease",
    "VpnHood.Client.Device.Android": "5.0.616-prerelease",
}


def write_restored_package(root: Path, package_id: str, version: str) -> None:
    package_dir = root / package_id.lower() / version.lower()
    package_dir.mkdir(parents=True)
    nupkg = package_dir / f"{package_id.lower()}.{version.lower()}.nupkg"
    nuspec = (
        '<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">'
        "<metadata>"
        f"<id>{package_id}</id><version>{version}</version>"
        '<repository type="git" url="https://github.com/vpnhood/VpnHood?token=redacted" '
        'commit="b4fec6567badcd0832e5157a6597f2b5b6b20fe0"/>'
        "</metadata></package>"
    )
    with zipfile.ZipFile(nupkg, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{package_id}.nuspec", nuspec)
    package_bytes = nupkg.read_bytes()
    content_hash = base64.b64encode(
        hashlib.sha512(package_bytes).digest()
    ).decode("ascii")
    (package_dir / ".nupkg.sha512").write_text(content_hash, encoding="utf-8")
    (package_dir / ".nupkg.metadata").write_text(
        json.dumps(
            {
                "version": 2,
                "contentHash": content_hash,
                "source": "https://build-user:secret@packages.example.test/v3/index.json?token=do-not-publish",
            }
        ),
        encoding="utf-8",
    )


class VpnHoodNuGetProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.packages = self.root / "packages"
        self.packages.mkdir()
        self.project = self.root / "GhostWeb.VpnHood.Android.csproj"
        refs = "".join(
            f'<PackageReference Include="{package_id}" Version="{version}" />'
            for package_id, version in PACKAGES.items()
        )
        self.project.write_text(
            f"<Project><ItemGroup>{refs}</ItemGroup></Project>", encoding="utf-8"
        )
        for package_id, version in PACKAGES.items():
            write_restored_package(self.packages, package_id, version)
        self.upstream = self.root / "vpnhood-upstream.sha"
        self.upstream.write_text(
            "b4fec6567badcd0832e5157a6597f2b5b6b20fe0\n", encoding="utf-8"
        )
        self.output = self.root / "VPNHOOD-NUGET-PACKAGES.txt"

    def tearDown(self):
        self.temp.cleanup()

    def run_recorder(self):
        return subprocess.run(
            [
                sys.executable,
                str(RECORDER),
                "--project",
                str(self.project),
                "--packages-dir",
                str(self.packages),
                "--upstream-revision-file",
                str(self.upstream),
                "--output",
                str(self.output),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_records_exact_package_hashes_and_separate_upstream_input(self):
        result = self.run_recorder()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.output.read_text(encoding="utf-8")
        self.assertIn(
            "Separate VpnHood upstream source checkout: b4fec6567badcd0832e5157a6597f2b5b6b20fe0",
            report,
        )
        self.assertIn(
            "not assumed to be the source commit for the NuGet package bytes", report
        )
        self.assertIn("Package: VpnHood.Client", report)
        self.assertIn("Package: VpnHood.Client.Device.Android", report)
        self.assertIn("NuGet source host: https://packages.example.test", report)
        self.assertIn(
            "Nuspec repository URL: https://github.com/vpnhood/VpnHood", report
        )
        self.assertIn(
            "Nuspec repository commit: b4fec6567badcd0832e5157a6597f2b5b6b20fe0",
            report,
        )
        self.assertNotIn("secret", report)
        self.assertNotIn("token=", report)

    def test_rejects_modified_nuget_content_hash(self):
        package_dir = self.packages / "vpnhood.client" / "5.0.616-prerelease"
        metadata_path = package_dir / ".nupkg.metadata"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["contentHash"] = "not-the-package-hash"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        result = self.run_recorder()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contentHash mismatch", result.stderr)

    def test_rejects_changed_package_version(self):
        project = self.project.read_text(encoding="utf-8")
        self.project.write_text(
            project.replace("5.0.616-prerelease", "5.0.617-prerelease", 1),
            encoding="utf-8",
        )
        result = self.run_recorder()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("version changed from reviewed pin", result.stderr)

    def test_release_and_compile_workflows_publish_the_provenance_report(self):
        release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        client = CLIENT_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("scripts/record-vpnhood-nuget-provenance.py", release)
        self.assertIn("scripts/record-vpnhood-nuget-provenance.py", client)
        self.assertIn("cp VPNHOOD-NUGET-PACKAGES.txt release/", release)
        self.assertIn("release/VPNHOOD-NUGET-PACKAGES.txt", release)
        self.assertIn("--pattern 'VPNHOOD-NUGET-PACKAGES.txt'", release)
        self.assertIn(
            "cmp -s release/VPNHOOD-NUGET-PACKAGES.txt verified-release/VPNHOOD-NUGET-PACKAGES.txt",
            release,
        )
        self.assertIn(
            "cp VPNHOOD-NUGET-PACKAGES.txt vpnhood-client-debug-artifact/", client
        )


if __name__ == "__main__":
    unittest.main()
