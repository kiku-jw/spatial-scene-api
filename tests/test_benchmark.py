from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.benchmark import (
    PRESETS,
    BenchmarkItem,
    BenchmarkSettings,
    build_gallery_html,
    build_render_plan,
    collect_benchmark_inputs,
)


class BenchmarkTests(unittest.TestCase):
    def test_collect_benchmark_inputs_only_keeps_supported_images(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        try:
            root = Path(temp_dir.name)
            (root / "portrait.png").write_bytes(b"fake")
            (root / "product.jpg").write_bytes(b"fake")
            (root / "notes.txt").write_text("skip", encoding="utf-8")

            inputs = collect_benchmark_inputs(root)

            self.assertEqual([path.name for path in inputs], ["portrait.png", "product.jpg"])
        finally:
            temp_dir.cleanup()

    def test_build_render_plan_creates_each_preset_for_each_input(self) -> None:
        settings = BenchmarkSettings(duration_seconds=1.0, fps=6, depth_provider="fallback")
        inputs = [Path("samples/benchmark/portrait.png"), Path("samples/benchmark/product.jpg")]

        plan = build_render_plan(inputs, Path("outputs/benchmark"), settings)

        self.assertEqual(len(plan), len(inputs) * len(PRESETS))
        self.assertEqual({job.preset for job in plan}, set(PRESETS))
        self.assertEqual(plan[0].output_path, Path("outputs/benchmark/portrait/orbit.mp4"))
        self.assertEqual(plan[-1].output_path, Path("outputs/benchmark/product/zoom_in_out.mp4"))

    def test_build_gallery_html_links_inputs_and_outputs(self) -> None:
        items = [
            BenchmarkItem(
                stem="portrait",
                input_path=Path("samples/benchmark/portrait.png"),
                depth_path=Path("outputs/benchmark/portrait/depth.png"),
                outputs={
                    "orbit": Path("outputs/benchmark/portrait/orbit.mp4"),
                    "zoom_in": Path("outputs/benchmark/portrait/zoom_in.mp4"),
                    "zoom_out": Path("outputs/benchmark/portrait/zoom_out.mp4"),
                    "zoom_in_out": Path("outputs/benchmark/portrait/zoom_in_out.mp4"),
                },
            )
        ]

        html = build_gallery_html(items, Path("outputs/benchmark"))

        self.assertIn("portrait", html)
        self.assertIn("../../samples/benchmark/portrait.png", html)
        self.assertIn("portrait/depth.png", html)
        self.assertEqual(html.count("<video"), 4)
        self.assertIn("portrait/zoom_out.mp4", html)
        self.assertIn("portrait/zoom_in_out.mp4", html)


if __name__ == "__main__":
    unittest.main()
