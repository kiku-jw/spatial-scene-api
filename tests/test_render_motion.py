from __future__ import annotations

import unittest

import numpy

from app.render import _coordinate_grid, _source_coordinates, build_settings


class RenderMotionTests(unittest.TestCase):
    def test_orbit_keeps_extra_crop_to_hide_corner_exposure(self) -> None:
        width = 180
        height = 100
        grid_x, grid_y = _coordinate_grid(width, height)
        depth_signed = numpy.zeros((height, width), dtype=numpy.float32)
        settings = build_settings(preset="orbit", strength="strong")

        source_x, _ = _source_coordinates(
            depth_signed,
            grid_x,
            grid_y,
            frame_index=0,
            frame_count=120,
            settings=settings,
            strength=1.0,
        )

        observed_zoom = (width - 1) / (float(source_x.max()) - float(source_x.min()))
        self.assertGreaterEqual(observed_zoom, 1.12)

    def test_orbit_depth_displacement_stays_below_artifact_prone_range(self) -> None:
        width = 180
        height = 100
        grid_x, grid_y = _coordinate_grid(width, height)
        settings = build_settings(preset="orbit", strength="strong")
        flat_depth = numpy.zeros((height, width), dtype=numpy.float32)
        near_depth = numpy.ones((height, width), dtype=numpy.float32)

        flat_x, _ = _source_coordinates(
            flat_depth,
            grid_x,
            grid_y,
            frame_index=30,
            frame_count=120,
            settings=settings,
            strength=1.0,
        )
        near_x, _ = _source_coordinates(
            near_depth,
            grid_x,
            grid_y,
            frame_index=30,
            frame_count=120,
            settings=settings,
            strength=1.0,
        )

        displacement = float(numpy.abs(flat_x - near_x).max())
        self.assertLessEqual(displacement, width * 0.035)

    def test_feedback_motion_pack_loops_without_seam(self) -> None:
        width = 180
        height = 100
        grid_x, grid_y = _coordinate_grid(width, height)
        depth_signed = numpy.linspace(-1.0, 1.0, width * height, dtype=numpy.float32).reshape((height, width))

        for preset in ("drift", "push_pull", "vertical_float"):
            with self.subTest(preset=preset):
                settings = build_settings(preset=preset, strength="strong")
                start_x, start_y = _source_coordinates(
                    depth_signed,
                    grid_x,
                    grid_y,
                    frame_index=0,
                    frame_count=121,
                    settings=settings,
                    strength=1.0,
                )
                quarter_x, quarter_y = _source_coordinates(
                    depth_signed,
                    grid_x,
                    grid_y,
                    frame_index=30,
                    frame_count=121,
                    settings=settings,
                    strength=1.0,
                )
                end_x, end_y = _source_coordinates(
                    depth_signed,
                    grid_x,
                    grid_y,
                    frame_index=120,
                    frame_count=121,
                    settings=settings,
                    strength=1.0,
                )

                numpy.testing.assert_allclose(start_x, end_x, atol=0.0001)
                numpy.testing.assert_allclose(start_y, end_y, atol=0.0001)
                self.assertGreater(float(numpy.abs(start_x - quarter_x).max()), 0.2)
                self.assertGreater(float(numpy.abs(start_y - quarter_y).max()), 0.2)


if __name__ == "__main__":
    unittest.main()
