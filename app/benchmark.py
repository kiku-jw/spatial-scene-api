from __future__ import annotations

import html
import json
import os
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy
from PIL import Image

from app.depth import create_depth_provider
from app.render import build_settings, prepare_scene, render_prepared_scene


PRESETS = ("orbit", "zoom_in", "zoom_out")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass(frozen=True)
class BenchmarkSettings:
    duration_seconds: float = 2.0
    fps: int = 12
    aspect_ratio: str = "9:16"
    strength: str = "safe"
    depth_provider: str = "fallback"


@dataclass(frozen=True)
class RenderJob:
    input_path: Path
    output_path: Path
    preset: str


@dataclass(frozen=True)
class BenchmarkItem:
    stem: str
    input_path: Path
    depth_path: Path
    outputs: dict[str, Path]


def collect_benchmark_inputs(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        return []
    paths = [
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    return sorted(paths, key=lambda path: path.name.lower())


def build_render_plan(
    input_paths: list[Path],
    output_root: Path,
    settings: BenchmarkSettings,
) -> list[RenderJob]:
    jobs: list[RenderJob] = []
    for input_path in input_paths:
        for preset in PRESETS:
            output_path = output_root / input_path.stem / f"{preset}.mp4"
            jobs.append(RenderJob(input_path=input_path, output_path=output_path, preset=preset))
    return jobs


def render_jobs(jobs: list[RenderJob], settings: BenchmarkSettings) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    provider = create_depth_provider(settings.depth_provider)
    grouped_jobs = _group_jobs_by_input(jobs)

    for input_path, input_jobs in grouped_jobs:
        scene_settings = build_settings(
            preset=input_jobs[0].preset,
            duration_seconds=settings.duration_seconds,
            fps=settings.fps,
            aspect_ratio=settings.aspect_ratio,
            strength=settings.strength,
            depth_provider=settings.depth_provider,
        )
        started_depth = perf_counter()
        scene = prepare_scene(input_path, scene_settings, provider)
        depth_elapsed_seconds = perf_counter() - started_depth
        depth_path = input_jobs[0].output_path.parent / "depth.png"
        write_depth_map(depth_path, scene.depth)

        for job in input_jobs:
            job.output_path.parent.mkdir(parents=True, exist_ok=True)
            render_settings = build_settings(
                preset=job.preset,
                duration_seconds=settings.duration_seconds,
                fps=settings.fps,
                aspect_ratio=settings.aspect_ratio,
                strength=settings.strength,
                depth_provider=settings.depth_provider,
            )
            started = perf_counter()
            render_prepared_scene(scene, job.output_path, render_settings)
            elapsed_seconds = perf_counter() - started
            results.append(
                {
                    "input": str(job.input_path),
                    "preset": job.preset,
                    "output": str(job.output_path),
                    "depth_map": str(depth_path),
                    "bytes": job.output_path.stat().st_size,
                    "elapsed_seconds": round(elapsed_seconds, 3),
                    "depth_elapsed_seconds": round(depth_elapsed_seconds, 3),
                }
            )
    return results


def write_depth_map(path: Path, depth: numpy.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray(numpy.clip(depth * 255.0, 0.0, 255.0).astype(numpy.uint8))
    image.save(path)


def _group_jobs_by_input(jobs: list[RenderJob]) -> list[tuple[Path, list[RenderJob]]]:
    groups: dict[Path, list[RenderJob]] = {}
    for job in jobs:
        groups.setdefault(job.input_path, []).append(job)
    return list(groups.items())


def _render_jobs_uncached(jobs: list[RenderJob], settings: BenchmarkSettings) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    provider = create_depth_provider(settings.depth_provider)
    for job in jobs:
        job.output_path.parent.mkdir(parents=True, exist_ok=True)
        render_settings = build_settings(
            preset=job.preset,
            duration_seconds=settings.duration_seconds,
            fps=settings.fps,
            aspect_ratio=settings.aspect_ratio,
            strength=settings.strength,
            depth_provider=settings.depth_provider,
        )
        started = perf_counter()
        scene = prepare_scene(job.input_path, render_settings, provider)
        render_prepared_scene(scene, job.output_path, render_settings)
        elapsed_seconds = perf_counter() - started
        results.append(
            {
                "input": str(job.input_path),
                "preset": job.preset,
                "output": str(job.output_path),
                "bytes": job.output_path.stat().st_size,
                "elapsed_seconds": round(elapsed_seconds, 3),
            }
        )
    return results


def build_benchmark_items(input_paths: list[Path], output_root: Path) -> list[BenchmarkItem]:
    items: list[BenchmarkItem] = []
    for input_path in input_paths:
        outputs = {
            preset: output_root / input_path.stem / f"{preset}.mp4"
            for preset in PRESETS
        }
        items.append(
            BenchmarkItem(
                stem=input_path.stem,
                input_path=input_path,
                depth_path=output_root / input_path.stem / "depth.png",
                outputs=outputs,
            )
        )
    return items


def write_manifest(
    manifest_path: Path,
    settings: BenchmarkSettings,
    render_results: list[dict[str, Any]],
) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "settings": {
            "duration_seconds": settings.duration_seconds,
            "fps": settings.fps,
            "aspect_ratio": settings.aspect_ratio,
            "strength": settings.strength,
            "depth_provider": settings.depth_provider,
        },
        "renders": render_results,
    }
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_gallery(gallery_path: Path, items: list[BenchmarkItem], base_dir: Path) -> None:
    gallery_path.parent.mkdir(parents=True, exist_ok=True)
    gallery_path.write_text(build_gallery_html(items, base_dir), encoding="utf-8")


def build_gallery_html(items: list[BenchmarkItem], base_dir: Path) -> str:
    rows = "\n".join(_build_gallery_row(item, base_dir) for item in items)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,">
    <title>Spatial Scene Benchmark Gallery</title>
    <style>
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: #f4f4f1;
        color: #222421;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        letter-spacing: 0;
      }}
      main {{
        width: min(1440px, calc(100vw - 28px));
        margin: 0 auto;
        padding: 24px 0 40px;
      }}
      header {{
        display: flex;
        align-items: end;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 16px;
      }}
      h1 {{
        margin: 0;
        font-size: 24px;
        line-height: 1.1;
      }}
      .meta {{
        color: #686a64;
        font-size: 13px;
      }}
      .case {{
        border-top: 1px solid #d8d5ce;
        padding: 18px 0 22px;
      }}
      .case h2 {{
        margin: 0 0 12px;
        font-size: 16px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: minmax(150px, 0.8fr) minmax(150px, 0.8fr) repeat(3, minmax(180px, 1fr));
        gap: 12px;
        align-items: start;
      }}
      figure {{
        margin: 0;
      }}
      figcaption {{
        margin-bottom: 6px;
        color: #62645f;
        font-size: 12px;
        font-weight: 700;
      }}
      img,
      video {{
        width: 100%;
        aspect-ratio: 9 / 16;
        display: block;
        border: 1px solid #d8d5ce;
        border-radius: 8px;
        background: #111;
        object-fit: contain;
      }}
      @media (max-width: 980px) {{
        .grid {{
          grid-template-columns: repeat(2, minmax(160px, 1fr));
        }}
      }}
      @media (max-width: 560px) {{
        main {{
          width: min(100vw - 18px, 420px);
        }}
        header {{
          align-items: start;
          flex-direction: column;
        }}
        .grid {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1>Spatial Scene Benchmark Gallery</h1>
        <div class="meta">Original image plus orbit, zoom_in, zoom_out renders</div>
      </header>
{rows}
    </main>
  </body>
</html>
"""


def _build_gallery_row(item: BenchmarkItem, base_dir: Path) -> str:
    original = _relative_path(item.input_path, base_dir)
    depth = _relative_path(item.depth_path, base_dir)
    videos = "\n".join(
        _video_figure(preset, _relative_path(item.outputs[preset], base_dir))
        for preset in PRESETS
    )
    title = html.escape(item.stem.replace("_", " "))
    return f"""      <section class="case">
        <h2>{title}</h2>
        <div class="grid">
          <figure>
            <figcaption>original</figcaption>
            <img src="{html.escape(original)}" alt="{title}">
          </figure>
          <figure>
            <figcaption>depth</figcaption>
            <img src="{html.escape(depth)}" alt="{title} depth">
          </figure>
{videos}
        </div>
      </section>"""


def _video_figure(label: str, path: str) -> str:
    return f"""          <figure>
            <figcaption>{html.escape(label)}</figcaption>
            <video src="{html.escape(path)}" controls muted loop playsinline preload="metadata"></video>
          </figure>"""


def _relative_path(path: Path, base_dir: Path) -> str:
    relative = os.path.relpath(path.resolve(), base_dir.resolve())
    return Path(relative).as_posix()
