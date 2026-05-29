from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy
from PIL import Image, ImageFilter


class DepthProvider(ABC):
    """Interface for swappable deterministic depth estimation."""

    @abstractmethod
    def estimate(self, image: Image.Image) -> numpy.ndarray:
        """Return a float32 depth map normalized to 0..1, foreground near 1."""


class DepthProviderUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class FallbackDepthProvider(DepthProvider):
    """Deterministic heuristic depth for the local MVP.

    It combines center bias, lower-frame bias, and local contrast, then smooths
    the result heavily so parallax stays subtle instead of jittery.
    """

    blur_radius: float = 18.0

    def estimate(self, image: Image.Image) -> numpy.ndarray:
        gray_image = image.convert("L")
        gray = numpy.array(gray_image, dtype=numpy.float32) / 255.0
        width, height = image.size

        soft_blur = numpy.array(
            gray_image.filter(ImageFilter.GaussianBlur(radius=5)),
            dtype=numpy.float32,
        ) / 255.0
        wide_blur = numpy.array(
            gray_image.filter(ImageFilter.GaussianBlur(radius=24)),
            dtype=numpy.float32,
        ) / 255.0

        saliency = _normalize(numpy.abs(gray - wide_blur))
        sharpness = _normalize(numpy.abs(gray - soft_blur))

        x_axis = numpy.linspace(0.0, 1.0, width, dtype=numpy.float32)
        y_axis = numpy.linspace(0.0, 1.0, height, dtype=numpy.float32)
        x_grid, y_grid = numpy.meshgrid(x_axis, y_axis)

        center_bias = numpy.exp(
            -(((x_grid - 0.5) ** 2.0) / 0.12 + ((y_grid - 0.52) ** 2.0) / 0.22)
        ).astype(numpy.float32)
        vertical_bias = numpy.clip(0.25 + y_grid * 0.75, 0.0, 1.0)

        depth = (
            center_bias * 0.48
            + vertical_bias * 0.24
            + saliency * 0.18
            + sharpness * 0.10
        )
        depth = _normalize(depth)

        depth_image = Image.fromarray(numpy.clip(depth * 255.0, 0.0, 255.0).astype(numpy.uint8))
        depth_image = depth_image.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))
        smoothed = numpy.array(depth_image, dtype=numpy.float32) / 255.0
        return _normalize(smoothed).astype(numpy.float32)


@dataclass
class DepthAnythingProvider(DepthProvider):
    """Optional real depth backend using Hugging Face Transformers.

    Dependencies are intentionally lazy so the local MVP still starts quickly
    with only the deterministic fallback installed.
    """

    model_name: str = "depth-anything/Depth-Anything-V2-Small-hf"
    device: int = -1
    _estimator: Any = None

    def estimate(self, image: Image.Image) -> numpy.ndarray:
        estimator = self._load_estimator()
        result = estimator(image)
        depth = self._extract_depth(result, image.size)
        return _normalize(depth).astype(numpy.float32)

    def _load_estimator(self) -> Any:
        if self._estimator is not None:
            return self._estimator

        try:
            from transformers import pipeline
        except ModuleNotFoundError:
            error = sys.exception()
            raise DepthProviderUnavailable(
                "Depth Anything backend requires optional dependencies. "
                "Install them with: python -m pip install -r requirements-depth.txt"
            ) from error

        try:
            self._estimator = pipeline(
                task="depth-estimation",
                model=self.model_name,
                device=self.device,
            )
        except Exception:
            error = sys.exception()
            raise DepthProviderUnavailable(
                f"Could not initialize depth model {self.model_name}: {error}"
            ) from error
        return self._estimator

    def _extract_depth(self, result: Any, size: tuple[int, int]) -> numpy.ndarray:
        if isinstance(result, dict):
            depth_image = result.get("depth")
            if isinstance(depth_image, Image.Image):
                resized = depth_image.convert("L").resize(size, Image.Resampling.BICUBIC)
                return numpy.array(resized, dtype=numpy.float32) / 255.0

            predicted_depth = result.get("predicted_depth")
            if predicted_depth is not None:
                return _tensor_like_to_depth(predicted_depth, size)

        raise DepthProviderUnavailable("Depth model returned an unsupported result shape")


def create_depth_provider(name: str | None = None) -> DepthProvider:
    normalized = (name or "fallback").strip().lower()
    fallback_names = {"fallback", "heuristic", "safe", "local"}
    depth_anything_names = {"depth_anything", "depth-anything", "depth_anything_v2", "real"}

    if normalized in fallback_names:
        return FallbackDepthProvider()
    if normalized in depth_anything_names:
        return DepthAnythingProvider()
    raise ValueError("depth_provider must be fallback or depth_anything")


def _tensor_like_to_depth(value: Any, size: tuple[int, int]) -> numpy.ndarray:
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()

    array = numpy.array(value, dtype=numpy.float32)
    array = numpy.squeeze(array)
    if array.ndim != 2:
        raise DepthProviderUnavailable("Depth tensor must be 2D after squeezing")

    image = Image.fromarray(numpy.clip(_normalize(array) * 255.0, 0.0, 255.0).astype(numpy.uint8))
    resized = image.resize(size, Image.Resampling.BICUBIC)
    return numpy.array(resized, dtype=numpy.float32) / 255.0


def _normalize(values: numpy.ndarray) -> numpy.ndarray:
    minimum = float(values.min())
    maximum = float(values.max())
    spread = maximum - minimum
    if spread < 0.000001:
        return numpy.full(values.shape, 0.5, dtype=numpy.float32)
    return ((values - minimum) / spread).astype(numpy.float32)
