from __future__ import annotations

import unittest

from app.depth import DepthAnythingProvider, FallbackDepthProvider, create_depth_provider
from app.render import build_settings


class DepthProviderTests(unittest.TestCase):
    def test_build_settings_keeps_depth_provider_choice(self) -> None:
        settings = build_settings(depth_provider="depth_anything")

        self.assertEqual(settings.depth_provider, "depth_anything")

    def test_build_settings_accepts_loopable_zoom_preset(self) -> None:
        settings = build_settings(preset="zoom_in_out")

        self.assertEqual(settings.preset, "zoom_in_out")

    def test_build_settings_accepts_feedback_motion_pack(self) -> None:
        for preset in ("drift", "push_pull", "vertical_float"):
            with self.subTest(preset=preset):
                settings = build_settings(preset=preset)

                self.assertEqual(settings.preset, preset)

    def test_depth_provider_factory_uses_fallback_by_default(self) -> None:
        provider = create_depth_provider("fallback")

        self.assertIsInstance(provider, FallbackDepthProvider)

    def test_depth_provider_factory_creates_lazy_depth_anything_provider(self) -> None:
        provider = create_depth_provider("depth_anything")

        self.assertIsInstance(provider, DepthAnythingProvider)

    def test_depth_provider_factory_rejects_unknown_provider(self) -> None:
        with self.assertRaises(ValueError):
            create_depth_provider("made_up")


if __name__ == "__main__":
    unittest.main()
