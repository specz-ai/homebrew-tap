"""Check public release gates without reading credentials or publishing assets."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from textwrap import dedent

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/release.yml"


class PublicReleaseTests(unittest.TestCase):
    """Protect public-only execution, candidate validation, and stable promotion."""

    def test_hosted_builds_use_only_public_inputs(self) -> None:
        """Keep private runners, repository credentials, and reusable calls out."""
        workflow = WORKFLOW.read_text()
        for forbidden in (
            "self-hosted",
            "HOMEBREW_TAP_TOKEN",
            "FLY_API_TOKEN",
            "workflow_call",
        ):
            self.assertNotIn(forbidden, workflow)
        self.assertIn("macos-15-intel", workflow)
        self.assertIn("runner: macos-15\n", workflow)
        self.assertNotIn("persist-credentials: true", workflow)
        self.assertEqual(workflow.count("      contents: write"), 2)

    def test_stable_publication_requires_verified_bottles(self) -> None:
        """Require both fresh-runner installations before changing stable metadata."""
        workflow = WORKFLOW.read_text()
        promote = workflow.split("  promote:\n", 1)[1]
        self.assertIn("needs: [prepare, verify-bottles]", promote)
        self.assertNotIn("if: always()", promote)
        self.assertIn("brew install --force-bottle", workflow)
        self.assertIn(".poured_from_bottle == true", workflow)
        self.assertIn("Refusing to downgrade", promote)
        self.assertEqual(workflow.count("git push"), 1)
        self.assertEqual(workflow.count("--prerelease=false"), 1)

    def test_candidate_versions_reject_injection(self) -> None:
        """Accept numeric versions and reject shell, path, and output injection."""
        step = WORKFLOW.read_text().split(
            "      - name: Validate candidate version\n", 1
        )[1]
        shell = dedent(step.split("        run: |\n", 1)[1].split("      - ", 1)[0])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            for version in (
                "0.5.3",
                "",
                "1.2",
                "../main",
                "1.2.3; echo unsafe",
                "1.2.3\nx=y",
            ):
                with self.subTest(version=version):
                    result = subprocess.run(
                        ["bash", "-c", shell],
                        env={
                            **os.environ,
                            "INPUT_VERSION": version,
                            "GITHUB_OUTPUT": str(output),
                        },
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=10,
                    )
                    self.assertEqual(result.returncode == 0, version == "0.5.3")
            self.assertEqual(output.read_text(), "value=0.5.3\n")


if __name__ == "__main__":
    unittest.main()
