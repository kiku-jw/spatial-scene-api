# Spatial Scene MVP Test Plan

## Static Checks

- Compile Python package with `python -m compileall app`.
- Confirm required packages import.

## Rendering Checks

- Generate a deterministic sample image.
- Render `orbit`, `zoom_in`, `zoom_out`, and `zoom_in_out`.
- Confirm MP4 files exist and are non-zero.
- Confirm ffprobe duration is close to requested duration.
- Generate benchmark samples with `python scripts/generate_benchmark_samples.py`.
- Render benchmark gallery with `python scripts/render_benchmark.py --duration-seconds 1 --fps 6 --depth-provider fallback`.
- Confirm `outputs/benchmark/gallery.html` references all cases and videos.
- After optional dependencies are installed, render a short `depth_provider=depth_anything` benchmark and confirm depth maps are generated.

## API Checks

- Start FastAPI locally.
- POST multipart image to `/api/render`.
- POST multipart image to `/v1/parallax`.
- POST with `depth_provider=fallback` and confirm MP4 output.
- POST with `depth_provider=depth_anything` without optional dependencies and confirm a clear 503 response.
- POST with `depth_provider=depth_anything` after optional dependencies are installed and confirm MP4 output.
- POST with `renderer=depthflow` after the isolated DepthFlow venv exists and confirm MP4 output.
- GET `/api/jobs/{job_id}` for a completed job.

## UI Checks

- Open `http://127.0.0.1:8000`.
- Upload sample image.
- Render one preset.
- Confirm preview video and download link appear.
- Select `renderer=depthflow`, render a short video, and confirm preview video/download link appear.
- Open `http://127.0.0.1:8000/outputs/benchmark/gallery.html`.
- Confirm all benchmark source images and videos load.
- Open an ML benchmark gallery and confirm original image, depth preview, and preset videos load for each case.
