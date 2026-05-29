# Spatial Scene / Parallax Video API

**Status:** parked public prototype. This repository is kept as a technical case study and reusable local MVP, not as an active SaaS production plan.

Local MVP for turning a single PNG/JPG/WebP image into a short deterministic MP4 with depth-style parallax. It does not call generative image-to-video models and does not rewrite image content.

## Browser Demo

Try the client-side demo:

```text
https://kiku-jw.github.io/spatial-scene-api/
```

The browser demo is static GitHub Pages. It does not upload images or use the FastAPI backend. Rendering runs on the visitor's device with Canvas and the browser video encoder. The optional **Experimental ML Depth** button downloads a small Transformers.js depth-estimation model into the browser cache and uses it locally. Depending on browser support, the download may be MP4 or WebM.

## Why This Is Parked

The prototype works, but the standalone SaaS opportunity is weak without stronger validation:

- The core effect is useful, but closer to a feature than a high-urgency paid product.
- Consumer tools already cover parts of the workflow.
- Better local output currently depends on DepthFlow, which is AGPL-3.0 and not suitable as-is for a closed commercial API.
- A commercial version would need either a clean-room renderer or a properly licensed rendering stack, plus clear unit economics for GPU/server cost.

The strongest future direction would be a broader batch video automation workflow, not a narrow parallax-only API. The public browser demo keeps the project useful as a portfolio artifact without requiring server infrastructure.

## What It Does

- Upload an image in the web UI.
- Choose `orbit`, `zoom_in`, or `zoom_out`.
- Render a 9:16 MP4, defaulting to 10 seconds at 30 FPS.
- Call the same renderer through `/api/render` or `/v1/parallax`.
- Use the default deterministic fallback depth provider, or opt into an optional Depth Anything backend.
- Optionally route rendering through an external DepthFlow renderer for higher-quality local parallax.
- Store uploads in `uploads/` and generated videos in `outputs/`.

## Requirements

- Python 3.11+
- FFmpeg and ffprobe available on `PATH`

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

Open the local DepthFlow-first UI mode:

```text
http://127.0.0.1:8000/?renderer=depthflow&strength=strong
```

## API

Multipart render endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/api/render" \
  -F "file=@samples/sample_scene.png" \
  -F "preset=orbit" \
  -F "duration_seconds=10" \
  -F "fps=30" \
  -F "aspect_ratio=9:16" \
  -F "strength=safe" \
  -F "renderer=internal" \
  -F "depth_provider=fallback"
```

API-compatible endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/v1/parallax" \
  -F "file=@samples/sample_scene.png" \
  -F "preset=zoom_in" \
  -F "duration_seconds=10" \
  -F "fps=30" \
  -F "aspect_ratio=9:16" \
  -F "strength=safe" \
  -F "renderer=internal" \
  -F "depth_provider=fallback"
```

`/v1/parallax` also accepts `image_url` instead of `file` for simple HTTP/HTTPS image fetching.

## Optional Real Depth

The default `depth_provider=fallback` is deterministic and requires no model downloads.

For a real monocular depth backend, install the optional dependencies:

```bash
python -m pip install -r requirements-depth.txt
```

Then call either API with:

```bash
-F "depth_provider=depth_anything"
```

This uses a lazy Hugging Face Transformers depth-estimation pipeline with `depth-anything/Depth-Anything-V2-Small-hf`. The first run may download model weights.

## Optional DepthFlow Renderer

The internal renderer is kept as a deterministic fallback. For better local spatial motion, the API can call DepthFlow as a separate external renderer.

DepthFlow is AGPL-3.0, so keep it isolated while evaluating product fit and license risk:

```bash
brew install portaudio
/opt/homebrew/bin/python3.11 -m venv .spikes/depthflow-venv
.spikes/depthflow-venv/bin/python -m pip install --upgrade pip setuptools wheel
.spikes/depthflow-venv/bin/python -m pip install depthflow==0.9.1 torch torchvision
```

Then call the API with:

```bash
curl -X POST "http://127.0.0.1:8000/v1/parallax" \
  -F "file=@samples/sample_scene.png" \
  -F "preset=orbit" \
  -F "duration_seconds=10" \
  -F "fps=30" \
  -F "aspect_ratio=9:16" \
  -F "strength=strong" \
  -F "renderer=depthflow"
```

The app looks for `DEPTHFLOW_BIN` first, then `.spikes/depthflow-venv/bin/depthflow`, then `depthflow` on `PATH`. On Apple Silicon, the wrapper sets `TORCH_DEVICE=mps` by default.

Local DepthFlow spike outputs, when generated, are served at:

```text
http://127.0.0.1:8000/outputs/depthflow_spike/full_10s/gallery.html
```

Example response:

```json
{
  "job_id": "abc123",
  "status": "done",
  "download_url": "/outputs/abc123.mp4",
  "preview_url": "/outputs/abc123.mp4"
}
```

Job lookup:

```bash
curl "http://127.0.0.1:8000/api/jobs/<job_id>"
```

## Benchmark Gallery

Generate a deterministic local benchmark pack:

```bash
python scripts/generate_benchmark_samples.py
```

Render every benchmark image through all three presets:

```bash
python scripts/render_benchmark.py --duration-seconds 1 --fps 6 --depth-provider fallback
```

Open the review gallery while the FastAPI server is running:

```text
http://127.0.0.1:8000/outputs/benchmark/gallery.html
```

Artifacts:

- `samples/benchmark/` - deterministic input images.
- `outputs/benchmark/` - rendered MP4s, `manifest.json`, and `gallery.html`.

For a more realistic quality pass, use:

```bash
python scripts/render_benchmark.py --duration-seconds 10 --fps 30 --depth-provider fallback
```

For an actual ML-depth spatial pass:

```bash
python -m pip install -r requirements-depth.txt
python scripts/render_benchmark.py \
  --input-dir /path/to/your/images \
  --output-dir outputs/your_images_ml_layers_benchmark \
  --gallery outputs/your_images_ml_layers_benchmark/gallery.html \
  --manifest outputs/your_images_ml_layers_benchmark/manifest.json \
  --duration-seconds 1 \
  --fps 6 \
  --depth-provider depth_anything \
  --strength strong
```

That gallery includes original image, ML depth preview, and the three rendered presets. This path uses depth-layer compositing and is much slower than the fallback renderer.

## Architecture

- `app/main.py` - FastAPI app, web UI route, upload/API endpoints.
- `app/render.py` - deterministic canvas preparation, parallax warping, FFmpeg MP4 encoding.
- `app/depthflow_external.py` - optional external DepthFlow CLI renderer wrapper.
- `app/depth.py` - swappable depth provider interface, fallback heuristic provider, optional Depth Anything provider.
- `app/jobs.py` - in-memory local job tracking.
- `app/static/index.html` - compact upload UI.
- `docs/index.html` - GitHub Pages browser-only demo.
- `app/benchmark.py` - benchmark planning, rendering, manifest, and gallery helpers.
- `scripts/generate_benchmark_samples.py` - deterministic sample image pack.
- `scripts/render_benchmark.py` - local benchmark runner.

## Current Limitations

- The default fallback depth is heuristic. It is stable and deterministic, but less accurate around complex subjects.
- `depth_provider=depth_anything` uses real ML depth estimation, then deterministic layered compositing. It does not use a generative video model.
- Rendering is synchronous. A request waits until FFmpeg finishes.
- A 10-second 720x1280 render can take tens of seconds on a local CPU.
- ML-depth layered rendering is more spatial, but much slower than fallback and can introduce edge halos around depth boundaries.
- DepthFlow output is much better and faster locally, but DepthFlow and ShaderFlow are AGPL-3.0. Treat this path as an isolated local spike until licensing is resolved.
- The GitHub Pages browser demo uses a lighter Canvas renderer. Its default heuristic depth is instant but rough; **Experimental ML Depth** improves the map locally at the cost of a first-run model download and slower setup.
- Browser demo export depends on browser encoder support, so output can be MP4 or WebM.
- No auth, billing, queues, webhooks, batch mode, or cloud deployment.
- Output resolution is currently tied to aspect ratio with 9:16 rendering at 720x1280.
- Wide or unusual source images are preserved with a blurred fill background to avoid black borders.

## Related Tools And References

- [DepthFlow](https://pypi.org/project/depthflow/) - high-quality local depth/parallax renderer used only as an optional external spike. License: AGPL-3.0.
- [ShaderFlow](https://github.com/BrokenSource/ShaderFlow) - rendering engine used by DepthFlow. License: AGPL-3.0.
- [Depth Anything V2 Small](https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf) - Apache-2.0 monocular depth model candidate for a cleaner commercial path.
- [Immersity AI](https://www.immersity.ai/pricing) and [Immersity API docs](https://docs-api.immersity.ai/docs/getting-started) - commercial 2D-to-3D / immersive motion product reference.
- [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/) - useful comparison point for generative image-to-video economics.
- [CapCut zoom templates](https://www.capcut.com/explore/Zoom-Effect) - consumer-side reference for the low-end/free alternative.

## Local Verification

Verified on 2026-05-28 and 2026-05-29:

- `python -m unittest discover -s tests`
- `python -m compileall app scripts tests`
- `POST /api/render` with `depth_provider=depth_anything`
- `POST /v1/parallax` with `depth_provider=depth_anything`
- `POST /v1/parallax` with `renderer=depthflow`
- Browser upload flow with `renderer=depthflow`, MP4 preview, and download link
- DepthFlow spike gallery with 3 source images and 9 MP4s
- `depth_provider=fallback` render path
- `depth_provider=depth_anything` ML render path
- `GET /api/jobs/{job_id}`
- Browser upload flow with MP4 preview and download link
- ffprobe confirmed generated smoke MP4s at 720x1280 with requested duration/FPS
- Benchmark gallery generated and browser-checked with 8 source images and 24 MP4s
- User-art ML layered benchmark browser-checked with 13 source images, 13 depth maps, and 39 MP4s
- GitHub Pages browser demo locally checked with client-side render and downloadable video output

## Next Best Step

Run the benchmark against real user/AI-generated image batches and use the gallery to tune preset strength, edge fill, and depth provider defaults.
