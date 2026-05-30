from __future__ import annotations

import unittest
from pathlib import Path

from app.depthflow_external import build_depthflow_command
from app.jobs import JobStore
from app.render import build_settings


class DepthFlowExternalTests(unittest.TestCase):
    def test_depthflow_command_uses_9x16_settings(self) -> None:
        settings = build_settings(
            preset="orbit",
            duration_seconds=10,
            fps=30,
            aspect_ratio="9:16",
            strength="strong",
        )

        command = build_depthflow_command(
            Path("/tmp/depthflow"),
            Path("input.png"),
            Path("output.mp4"),
            settings,
        )

        self.assertIn("orbital", command)
        self.assertIn("--ratio", command)
        self.assertIn("9:16", command)
        self.assertIn("-h", command)
        self.assertIn("1280", command)
        self.assertIn("30", command)
        self.assertIn("10.0", command)
        self.assertEqual(command[-1], "--no-turbo")

    def test_depthflow_zoom_out_command_reverses_motion(self) -> None:
        settings = build_settings(preset="zoom_out", strength="medium")

        command = build_depthflow_command(
            Path("/tmp/depthflow"),
            Path("input.png"),
            Path("output.mp4"),
            settings,
        )

        self.assertIn("zoom", command)
        self.assertIn("horizontal", command)
        self.assertEqual(command.count("--reverse"), 2)

    def test_depthflow_zoom_in_out_command_keeps_looping_motion(self) -> None:
        settings = build_settings(preset="zoom_in_out", strength="medium")

        command = build_depthflow_command(
            Path("/tmp/depthflow"),
            Path("input.png"),
            Path("output.mp4"),
            settings,
        )

        self.assertIn("zoom", command)
        self.assertIn("horizontal", command)
        self.assertNotIn("--no-loop", command)
        self.assertNotIn("--reverse", command)

    def test_depthflow_feedback_motion_pack_uses_supported_presets(self) -> None:
        expected_components = {
            "drift": ("horizontal", "vertical"),
            "push_pull": ("dolly", "horizontal"),
            "vertical_float": ("vertical", "horizontal"),
        }
        for preset, components in expected_components.items():
            with self.subTest(preset=preset):
                settings = build_settings(preset=preset, strength="medium")
                command = build_depthflow_command(
                    Path("/tmp/depthflow"),
                    Path("input.png"),
                    Path("output.mp4"),
                    settings,
                )

                for component in components:
                    self.assertIn(component, command)
                self.assertNotIn("--no-loop", command)

    def test_depthflow_feedback_motion_pack_responds_to_strength(self) -> None:
        for preset in ("drift", "push_pull", "vertical_float"):
            with self.subTest(preset=preset):
                safe_command = build_depthflow_command(
                    Path("/tmp/depthflow"),
                    Path("input.png"),
                    Path("output.mp4"),
                    build_settings(preset=preset, strength="safe"),
                )
                strong_command = build_depthflow_command(
                    Path("/tmp/depthflow"),
                    Path("input.png"),
                    Path("output.mp4"),
                    build_settings(preset=preset, strength="strong"),
                )

                self.assertNotEqual(safe_command, strong_command)

    def test_job_record_includes_renderer(self) -> None:
        store = JobStore()
        record = store.create(
            job_id="job-1",
            preset="orbit",
            duration_seconds=10,
            fps=30,
            aspect_ratio="9:16",
            strength="safe",
            renderer="depthflow",
            depth_provider="depth_anything",
        )

        self.assertEqual(record.to_dict()["renderer"], "depthflow")


if __name__ == "__main__":
    unittest.main()
