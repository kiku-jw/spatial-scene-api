from __future__ import annotations

import unittest
from pathlib import Path
from struct import unpack


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "docs" / "index.html"
DEMO_IMAGE = ROOT / "docs" / "assets" / "demo.png"


class BrowserDemoStaticTests(unittest.TestCase):
    def test_demo_image_is_a_real_static_asset(self) -> None:
        self.assertTrue(DEMO_IMAGE.exists())
        self.assertGreater(DEMO_IMAGE.stat().st_size, 1024 * 1024)
        width, height = read_png_size(DEMO_IMAGE)
        self.assertEqual((width, height), (1672, 941))

    def test_demo_page_loads_static_demo_image(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn("assets/demo.png", html)
        self.assertIn("loadDemoImageFromAsset", html)

    def test_rendered_preview_video_loops(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn('<video id="video" controls playsinline loop>', html)

    def test_ml_depth_is_prepared_by_default_with_honest_fallback(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn("startAutoMlDepth", html)
        self.assertIn("ensurePreferredDepthReady", html)
        self.assertIn("ML depth unavailable. Heuristic depth is active.", html)

    def test_renderer_uses_fine_mesh_and_high_quality_export(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn('<option value="1920x1080" selected>', html)
        self.assertIn("const DEPTH_BASE_SIZE = 256", html)
        self.assertIn("function getTileSize", html)
        self.assertIn("function getVideoBitrate", html)
        self.assertIn('imageSmoothingQuality = "high"', html)
        self.assertNotIn("const size = width >= 720 ? 24 : 20", html)


def read_png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as png:
        header = png.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Expected a PNG file.")
    return unpack(">II", header[16:24])


if __name__ == "__main__":
    unittest.main()
