from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError

from app.depth import DepthProvider, create_depth_provider


ALLOWED_PRESETS = {
    "drift",
    "orbit",
    "push_pull",
    "vertical_float",
    "zoom_in",
    "zoom_in_out",
    "zoom_out",
}
DEFAULT_OUTPUT_HEIGHT = 1280


class RenderError(RuntimeError):
    pass


@dataclass(frozen=True)
class RenderSettings:
    preset: str = "orbit"
    duration_seconds: float = 10.0
    fps: int = 30
    aspect_ratio: str = "9:16"
    strength: str = "safe"
    depth_provider: str = "fallback"
    width: int = 720
    height: int = 1280


@dataclass(frozen=True)
class PreparedScene:
    base_array: numpy.ndarray
    depth: numpy.ndarray


def build_settings(
    preset: str = "orbit",
    duration_seconds: float = 10.0,
    fps: int = 30,
    aspect_ratio: str = "9:16",
    strength: str = "safe",
    depth_provider: str = "fallback",
) -> RenderSettings:
    normalized_preset = preset.strip().lower()
    if normalized_preset not in ALLOWED_PRESETS:
        raise ValueError(f"preset must be one of: {', '.join(sorted(ALLOWED_PRESETS))}")

    safe_duration = float(duration_seconds)
    if safe_duration < 1.0 or safe_duration > 30.0:
        raise ValueError("duration_seconds must be between 1 and 30")

    safe_fps = int(fps)
    if safe_fps < 6 or safe_fps > 60:
        raise ValueError("fps must be between 6 and 60")

    width, height = _dimensions_for_aspect_ratio(aspect_ratio)
    return RenderSettings(
        preset=normalized_preset,
        duration_seconds=safe_duration,
        fps=safe_fps,
        aspect_ratio=aspect_ratio,
        strength=strength.strip().lower() or "safe",
        depth_provider=_normalize_depth_provider_name(depth_provider),
        width=width,
        height=height,
    )


def render_parallax_video(
    input_path: Path,
    output_path: Path,
    settings: RenderSettings,
    depth_provider: DepthProvider | None = None,
) -> Path:
    scene = prepare_scene(input_path, settings, depth_provider)
    render_prepared_scene(scene, output_path, settings)
    return output_path


def prepare_scene(
    input_path: Path,
    settings: RenderSettings,
    depth_provider: DepthProvider | None = None,
) -> PreparedScene:
    provider = depth_provider or create_depth_provider(settings.depth_provider)
    source = _load_rgb_image(input_path)
    canvas = _compose_canvas(source, settings.width, settings.height)
    source.close()

    depth = provider.estimate(canvas)
    base_array = numpy.array(canvas, dtype=numpy.float32)
    canvas.close()

    return PreparedScene(base_array=base_array, depth=depth)


def render_prepared_scene(
    scene: PreparedScene,
    output_path: Path,
    settings: RenderSettings,
) -> Path:
    _encode_video(scene.base_array, scene.depth, output_path, settings)
    return output_path


def _load_rgb_image(input_path: Path) -> Image.Image:
    try:
        opened = Image.open(input_path)
        opened.load()
    except UnidentifiedImageError:
        raise RenderError("Input file is not a readable PNG, JPG, or WebP image")

    transposed = ImageOps.exif_transpose(opened)
    opened.close()
    if transposed.mode in {"RGBA", "LA"}:
        background = Image.new("RGB", transposed.size, (245, 245, 242))
        alpha = transposed.getchannel("A")
        background.paste(transposed.convert("RGB"), (0, 0), alpha)
        transposed.close()
        return background
    return transposed.convert("RGB")


def _compose_canvas(image: Image.Image, width: int, height: int) -> Image.Image:
    background = _resize_cover(image, width, height)
    background = background.filter(ImageFilter.GaussianBlur(radius=34))
    background = ImageEnhance.Brightness(background).enhance(0.78)
    background = ImageEnhance.Contrast(background).enhance(0.88)

    foreground = _resize_contain(image, width, height)
    x_position = (width - foreground.width) // 2
    y_position = (height - foreground.height) // 2
    background.paste(foreground, (x_position, y_position))
    foreground.close()
    return background


def _resize_cover(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = max(width / image.width, height / image.height)
    resized_width = max(width, int(round(image.width * scale)))
    resized_height = max(height, int(round(image.height * scale)))
    resized = image.resize((resized_width, resized_height), Image.Resampling.LANCZOS)
    left = (resized_width - width) // 2
    top = (resized_height - height) // 2
    covered = resized.crop((left, top, left + width, top + height))
    resized.close()
    return covered


def _resize_contain(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = min(width / image.width, height / image.height)
    resized_width = max(2, int(round(image.width * scale)))
    resized_height = max(2, int(round(image.height * scale)))
    return image.resize((resized_width, resized_height), Image.Resampling.LANCZOS)


def _encode_video(
    base_array: numpy.ndarray,
    depth: numpy.ndarray,
    output_path: Path,
    settings: RenderSettings,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame_count = max(1, int(round(settings.duration_seconds * settings.fps)))
    height, width = base_array.shape[:2]
    grid_x, grid_y = _coordinate_grid(width, height)
    depth_signed = ((depth - 0.5) * 2.0).astype(numpy.float32)
    strength = _strength_factor(settings.strength)

    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        str(settings.fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdin is None:
        raise RenderError("Could not open ffmpeg stdin")

    for frame_index in range(frame_count):
        frame = _render_frame(
            base_array=base_array,
            depth_signed=depth_signed,
            grid_x=grid_x,
            grid_y=grid_y,
            frame_index=frame_index,
            frame_count=frame_count,
            settings=settings,
            strength=strength,
        )
        process.stdin.write(frame.tobytes())

    process.stdin.close()
    stderr = b""
    if process.stderr is not None:
        stderr = process.stderr.read()
    return_code = process.wait()
    if return_code != 0:
        message = stderr.decode("utf-8", errors="replace").strip()
        raise RenderError(message or "ffmpeg failed")


def _render_frame(
    base_array: numpy.ndarray,
    depth_signed: numpy.ndarray,
    grid_x: numpy.ndarray,
    grid_y: numpy.ndarray,
    frame_index: int,
    frame_count: int,
    settings: RenderSettings,
    strength: float,
) -> numpy.ndarray:
    if settings.depth_provider == "depth_anything":
        return _render_layered_frame(
            base_array=base_array,
            depth_signed=depth_signed,
            grid_x=grid_x,
            grid_y=grid_y,
            frame_index=frame_index,
            frame_count=frame_count,
            settings=settings,
            strength=strength,
        )
    return _render_warped_frame(
        base_array=base_array,
        depth_signed=depth_signed,
        grid_x=grid_x,
        grid_y=grid_y,
        frame_index=frame_index,
        frame_count=frame_count,
        settings=settings,
        strength=strength,
    )


def _render_warped_frame(
    base_array: numpy.ndarray,
    depth_signed: numpy.ndarray,
    grid_x: numpy.ndarray,
    grid_y: numpy.ndarray,
    frame_index: int,
    frame_count: int,
    settings: RenderSettings,
    strength: float,
) -> numpy.ndarray:
    source_x, source_y = _source_coordinates(
        depth_signed=depth_signed,
        grid_x=grid_x,
        grid_y=grid_y,
        frame_index=frame_index,
        frame_count=frame_count,
        settings=settings,
        strength=strength,
    )
    sampled = _sample_bilinear(base_array, source_x, source_y)
    return numpy.clip(sampled + 0.5, 0.0, 255.0).astype(numpy.uint8)


def _render_layered_frame(
    base_array: numpy.ndarray,
    depth_signed: numpy.ndarray,
    grid_x: numpy.ndarray,
    grid_y: numpy.ndarray,
    frame_index: int,
    frame_count: int,
    settings: RenderSettings,
    strength: float,
) -> numpy.ndarray:
    depth = (depth_signed + 1.0) * 0.5
    layer_edges = (0.0, 0.22, 0.40, 0.58, 0.76, 1.01)
    background_depth = numpy.full(depth.shape, -1.0, dtype=numpy.float32)
    source_x, source_y = _source_coordinates(
        depth_signed=background_depth,
        grid_x=grid_x,
        grid_y=grid_y,
        frame_index=frame_index,
        frame_count=frame_count,
        settings=settings,
        strength=strength,
    )
    composed = _sample_bilinear(base_array, source_x, source_y)

    for layer_index in range(len(layer_edges) - 1):
        low = layer_edges[layer_index]
        high = layer_edges[layer_index + 1]
        center = (low + high) * 0.5
        layer_mask = numpy.logical_and(depth >= low, depth < high).astype(numpy.float32)
        layer_mask = _soften_mask(layer_mask)
        layer_depth = numpy.full(depth.shape, center * 2.0 - 1.0, dtype=numpy.float32)
        layer_source_x, layer_source_y = _source_coordinates(
            depth_signed=layer_depth,
            grid_x=grid_x,
            grid_y=grid_y,
            frame_index=frame_index,
            frame_count=frame_count,
            settings=settings,
            strength=strength,
        )
        layer_rgb = _sample_bilinear(base_array, layer_source_x, layer_source_y)
        layer_alpha = _sample_bilinear(
            layer_mask[..., None],
            layer_source_x,
            layer_source_y,
        )[..., 0]
        layer_alpha = numpy.clip(layer_alpha, 0.0, 1.0)
        composed = layer_rgb * layer_alpha[..., None] + composed * (1.0 - layer_alpha[..., None])

    return numpy.clip(composed + 0.5, 0.0, 255.0).astype(numpy.uint8)


def _source_coordinates(
    depth_signed: numpy.ndarray,
    grid_x: numpy.ndarray,
    grid_y: numpy.ndarray,
    frame_index: int,
    frame_count: int,
    settings: RenderSettings,
    strength: float,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    height, width = depth_signed.shape[:2]
    center_x = (width - 1) / 2.0
    center_y = (height - 1) / 2.0
    centered_x = grid_x - center_x
    centered_y = grid_y - center_y
    progress = frame_index / max(1, frame_count - 1)

    zoom = 1.04
    pan_x = 0.0
    pan_y = 0.0
    shift_x = numpy.zeros((height, width), dtype=numpy.float32)
    shift_y = numpy.zeros((height, width), dtype=numpy.float32)

    if settings.preset == "orbit":
        phase = math.sin((frame_index / max(1, frame_count)) * math.tau)
        lift = math.cos((frame_index / max(1, frame_count)) * math.tau)
        orbit_strength = strength * 0.72
        zoom = 1.125 + (1.0 - lift) * 0.006
        shift_x = depth_signed * phase * width * 0.040 * orbit_strength
        shift_y = depth_signed * -phase * height * 0.0045 * orbit_strength
        pan_x = phase * width * 0.008 * orbit_strength
    elif settings.preset == "zoom_in":
        eased = _smoothstep(progress)
        zoom = 1.025 + eased * 0.105
        radial_strength = (0.2 + eased * 0.8) * width * 0.010 * strength
        shift_x = (centered_x / max(1.0, center_x)) * depth_signed * radial_strength
        shift_y = (centered_y / max(1.0, center_y)) * depth_signed * radial_strength
        pan_y = -eased * height * 0.004 * strength
    elif settings.preset == "zoom_in_out":
        cycle = 0.5 - 0.5 * math.cos(progress * math.tau)
        sway = math.sin(progress * math.tau)
        zoom = 1.025 + cycle * 0.105
        radial_strength = (0.2 + cycle * 0.8) * width * 0.010 * strength
        shift_x = (centered_x / max(1.0, center_x)) * depth_signed * radial_strength
        shift_y = (centered_y / max(1.0, center_y)) * depth_signed * radial_strength
        pan_x = sway * width * 0.004 * strength
        pan_y = -sway * height * 0.003 * strength
    elif settings.preset == "drift":
        sway = math.sin(progress * math.tau)
        zoom = 1.09
        shift_x = depth_signed * sway * width * 0.024 * strength
        shift_y = depth_signed * -sway * height * 0.010 * strength
        pan_x = sway * width * 0.006 * strength
        pan_y = -sway * height * 0.004 * strength
    elif settings.preset == "push_pull":
        cycle = 0.5 - 0.5 * math.cos(progress * math.tau)
        sway = math.sin(progress * math.tau)
        zoom = 1.055 + cycle * 0.095
        radial_strength = (0.35 + cycle * 0.8) * width * 0.012 * strength
        shift_x = (centered_x / max(1.0, center_x)) * depth_signed * radial_strength
        shift_y = (centered_y / max(1.0, center_y)) * depth_signed * radial_strength
        pan_x = sway * width * 0.003 * strength
        pan_y = -sway * height * 0.002 * strength
    elif settings.preset == "vertical_float":
        sway = math.sin(progress * math.tau)
        zoom = 1.095
        shift_x = depth_signed * sway * width * 0.006 * strength
        shift_y = depth_signed * sway * height * 0.028 * strength
        pan_x = sway * width * 0.002 * strength
        pan_y = sway * height * 0.008 * strength
    elif settings.preset == "zoom_out":
        eased = _smoothstep(progress)
        zoom = 1.13 - eased * 0.105
        radial_strength = (1.0 - eased * 0.65) * width * 0.010 * strength
        shift_x = (centered_x / max(1.0, center_x)) * depth_signed * radial_strength
        shift_y = (centered_y / max(1.0, center_y)) * depth_signed * radial_strength
        pan_y = eased * height * 0.004 * strength

    source_x = centered_x / zoom + center_x - pan_x - shift_x
    source_y = centered_y / zoom + center_y - pan_y - shift_y
    return source_x, source_y


def _soften_mask(mask: numpy.ndarray) -> numpy.ndarray:
    mask_image = Image.fromarray(numpy.clip(mask * 255.0, 0.0, 255.0).astype(numpy.uint8))
    softened = mask_image.filter(ImageFilter.GaussianBlur(radius=5))
    return numpy.array(softened, dtype=numpy.float32) / 255.0


def _sample_bilinear(image: numpy.ndarray, x_coordinates: numpy.ndarray, y_coordinates: numpy.ndarray) -> numpy.ndarray:
    height, width = image.shape[:2]
    clipped_x = numpy.clip(x_coordinates, 0.0, width - 1.0)
    clipped_y = numpy.clip(y_coordinates, 0.0, height - 1.0)

    x0 = numpy.floor(clipped_x).astype(numpy.int32)
    y0 = numpy.floor(clipped_y).astype(numpy.int32)
    x1 = numpy.clip(x0 + 1, 0, width - 1)
    y1 = numpy.clip(y0 + 1, 0, height - 1)

    dx = (clipped_x - x0).astype(numpy.float32)
    dy = (clipped_y - y0).astype(numpy.float32)

    top_left = image[y0, x0]
    top_right = image[y0, x1]
    bottom_left = image[y1, x0]
    bottom_right = image[y1, x1]

    top = top_left * (1.0 - dx[..., None]) + top_right * dx[..., None]
    bottom = bottom_left * (1.0 - dx[..., None]) + bottom_right * dx[..., None]
    return top * (1.0 - dy[..., None]) + bottom * dy[..., None]


def _coordinate_grid(width: int, height: int) -> tuple[numpy.ndarray, numpy.ndarray]:
    x_axis = numpy.arange(width, dtype=numpy.float32)
    y_axis = numpy.arange(height, dtype=numpy.float32)
    return numpy.meshgrid(x_axis, y_axis)


def _smoothstep(value: float) -> float:
    clipped = min(1.0, max(0.0, value))
    return clipped * clipped * (3.0 - 2.0 * clipped)


def _strength_factor(strength: str) -> float:
    normalized = strength.strip().lower()
    named_strengths = {
        "safe": 0.72,
        "subtle": 0.72,
        "soft": 0.55,
        "medium": 1.0,
        "normal": 1.0,
        "strong": 1.25,
    }
    if normalized in named_strengths:
        return named_strengths[normalized]
    try:
        numeric = float(normalized)
    except ValueError:
        return named_strengths["safe"]
    return min(1.5, max(0.2, numeric))


def _dimensions_for_aspect_ratio(aspect_ratio: str) -> tuple[int, int]:
    parts = aspect_ratio.strip().lower().replace("x", ":").split(":")
    if len(parts) != 2:
        raise ValueError("aspect_ratio must look like 9:16")
    width_part = float(parts[0])
    height_part = float(parts[1])
    if width_part <= 0 or height_part <= 0:
        raise ValueError("aspect_ratio values must be positive")

    if width_part <= height_part:
        height = DEFAULT_OUTPUT_HEIGHT
        width = int(round(height * (width_part / height_part)))
    else:
        width = DEFAULT_OUTPUT_HEIGHT
        height = int(round(width * (height_part / width_part)))
    return _even(width), _even(height)


def _normalize_depth_provider_name(depth_provider: str) -> str:
    normalized = depth_provider.strip().lower() or "fallback"
    if normalized in {"fallback", "heuristic", "safe", "local"}:
        return "fallback"
    if normalized in {"depth_anything", "depth-anything", "depth_anything_v2", "real"}:
        return "depth_anything"
    raise ValueError("depth_provider must be fallback or depth_anything")


def _even(value: int) -> int:
    if value % 2 == 0:
        return value
    return value + 1
