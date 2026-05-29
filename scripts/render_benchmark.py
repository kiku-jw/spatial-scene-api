from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.benchmark import (
    BenchmarkSettings,
    build_benchmark_items,
    build_render_plan,
    collect_benchmark_inputs,
    render_jobs,
    write_gallery,
    write_manifest,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Spatial Scene benchmark videos.")
    parser.add_argument("--input-dir", default="samples/benchmark")
    parser.add_argument("--output-dir", default="outputs/benchmark")
    parser.add_argument("--duration-seconds", type=float, default=2.0)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--aspect-ratio", default="9:16")
    parser.add_argument("--strength", default="safe")
    parser.add_argument("--depth-provider", default="fallback")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--gallery", default="outputs/benchmark/gallery.html")
    parser.add_argument("--manifest", default="outputs/benchmark/manifest.json")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    input_paths = collect_benchmark_inputs(input_dir)
    if args.limit > 0:
        input_paths = input_paths[: args.limit]
    if not input_paths:
        raise SystemExit(f"No benchmark images found in {input_dir}")

    settings = BenchmarkSettings(
        duration_seconds=args.duration_seconds,
        fps=args.fps,
        aspect_ratio=args.aspect_ratio,
        strength=args.strength,
        depth_provider=args.depth_provider,
    )
    jobs = build_render_plan(input_paths, output_dir, settings)
    if args.skip_existing:
        jobs = [job for job in jobs if not job.output_path.exists()]

    results = render_jobs(jobs, settings)
    items = build_benchmark_items(input_paths, output_dir)
    write_manifest(Path(args.manifest), settings, results)
    gallery_path = Path(args.gallery)
    write_gallery(gallery_path, items, gallery_path.parent)

    print(f"Images: {len(input_paths)}")
    print(f"Rendered: {len(results)}")
    print(f"Gallery: {args.gallery}")
    print(f"Manifest: {args.manifest}")


if __name__ == "__main__":
    main()
