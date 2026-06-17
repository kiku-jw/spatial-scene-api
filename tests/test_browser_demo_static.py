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

    def test_empty_preview_plus_opens_image_picker(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn('<button class="empty" id="emptyState" type="button">', html)
        self.assertIn('emptyState.addEventListener("click"', html)
        self.assertIn("imageInput.click()", html)

    def test_rendered_preview_video_loops(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn('<video id="video" controls playsinline autoplay muted loop>', html)
        self.assertIn("playRenderedPreview", html)
        self.assertIn("video.play()", html)

    def test_ml_depth_is_prepared_by_default_with_honest_fallback(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn("startAutoMlDepth", html)
        self.assertIn("ensurePreferredDepthReady", html)
        self.assertIn("ML depth unavailable. Heuristic depth is active.", html)

    def test_renderer_uses_fine_mesh_and_high_quality_export(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn('<option value="zoom_in_out">zoom_in_out</option>', html)
        self.assertIn('if (preset === "zoom_in_out")', html)
        self.assertIn("const pingPong = 0.5 - 0.5 * Math.cos(progress * Math.PI * 2);", html)
        self.assertIn('<option value="1920x1080" selected>', html)
        self.assertIn('<input id="fps" type="number" min="8" max="30" step="1" value="30">', html)
        self.assertIn("const fps = clamp(Number(fpsInput.value) || 30, 8, 30);", html)
        self.assertIn("const DEPTH_BASE_SIZE = 256", html)
        self.assertIn("function getTileSize", html)
        self.assertIn("function getVideoBitrate", html)
        self.assertIn('imageSmoothingQuality = "high"', html)
        self.assertNotIn("const size = width >= 720 ? 24 : 20", html)

    def test_orbit_renderer_uses_extra_overscan_and_tamer_depth_motion(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn("const orbitStrength = strength * 0.72;", html)
        self.assertIn("globalScale: 1.095", html)
        self.assertIn("depthZoom: orbitStrength * 0.045", html)
        self.assertIn("depthWeight: 0.82", html)
        self.assertIn("return Math.max(1.15, Math.min(3.2", html)

    def test_renderer_offers_feedback_motion_pack(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        for preset in ("drift", "push_pull", "vertical_float"):
            self.assertIn(f'<option value="{preset}">{preset}</option>', html)
            self.assertIn(f'if (preset === "{preset}")', html)

    def test_pro_fake_door_collects_purchase_intent_without_unlocking_render(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn('id="proButton"', html)
        self.assertIn('id="proDialog"', html)
        self.assertIn('id="proInterestForm"', html)
        self.assertIn('trackEvent("pro_click"', html)
        self.assertIn('trackEvent("pro_interest_submit"', html)
        self.assertIn("Pro export is a validation waitlist in this build.", html)

    def test_browser_analytics_are_privacy_safe_and_endpoint_ready(self) -> None:
        html = INDEX_HTML.read_text(encoding="utf-8")

        self.assertIn("KIKU_SPATIAL_ANALYTICS_ENDPOINT", html)
        self.assertIn("trackEvent", html)
        self.assertIn("spatial-scene-events", html)
        self.assertIn('trackEvent("image_loaded"', html)
        self.assertIn('trackEvent("render_success"', html)
        self.assertIn('trackEvent("download_click"', html)
        self.assertNotIn("fileContent", html)
        self.assertNotIn("videoBlob", html)


def read_png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as png:
        header = png.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Expected a PNG file.")
    return unpack(">II", header[16:24])


if __name__ == "__main__":
    unittest.main()
