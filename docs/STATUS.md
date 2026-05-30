# Spatial Scene MVP Status

## 2026-05-28

- Repository started nearly empty.
- Chosen stack: FastAPI, Pillow, NumPy, FFmpeg.
- OpenCV and paid/generative video APIs intentionally excluded from MVP.
- Implementation complete for local MVP.
- Verified `/api/render`, `/v1/parallax`, job lookup, and browser upload preview.
- Generated 10-second sample MP4s for `orbit`, `zoom_in`, and `zoom_out`.
- Known tradeoff: synchronous CPU rendering is simple but not fast.
- Added optional `depth_provider=depth_anything` backend behind a lazy provider, with fallback remaining the default.
- Added benchmark sample generator, benchmark runner, manifest output, and HTML review gallery.
- Browser-verified benchmark gallery with 8 input images and 24 rendered MP4s.
- Installed optional `depth_anything` dependencies and verified real ML depth estimation.
- Added cached depth preparation and depth preview PNGs for benchmark galleries.
- Added layered compositing for `depth_provider=depth_anything`; this is more spatial than fallback but CPU-expensive.
- Browser-verified local-image ML layered benchmark with 13 input images, 13 depth maps, and 39 rendered MP4s.
- Reviewed deep research report and confirmed the quality issue is architectural: the renderer needs better DIBR/mesh/LDI-style scene representation and disocclusion handling, not just stronger warping.
- Added `docs/RENDERER_RESEARCH.md` with the next renderer decision: spike DepthFlow externally first, keep current renderer as fallback, avoid folding AGPL/non-commercial research code into core.
- Installed DepthFlow in isolated `.spikes/depthflow-venv` with PyTorch/MPS on Apple M3 and verified headless OpenGL rendering.
- Generated DepthFlow 9:16 10-second/30 FPS sample videos for three local test images and all three presets under `outputs/depthflow_spike/full_10s`.
- Added optional `renderer=depthflow` API/UI path that invokes DepthFlow as an external CLI renderer while preserving the existing internal renderer as default.

## 2026-05-29

- Verified the running local API with `renderer=depthflow` through `/v1/parallax`; output was 720x1280, 2 seconds, 12 FPS, 24 frames.
- Browser-verified the UI upload flow with `renderer=depthflow`, including video preview metadata and download link.
- Browser-verified `outputs/depthflow_spike/full_10s/gallery.html`: 3 source images, 9 videos, all metadata-loaded at 720x1280 and 10 seconds.
- ffprobe-confirmed all DepthFlow spike videos in `outputs/depthflow_spike/full_10s` are 720x1280, 30 FPS, 300 frames, and 10 seconds.
- Added a browser-only GitHub Pages demo in `docs/index.html`; it renders locally with Canvas and MediaRecorder on the visitor's device.
- Added `zoom_in_out`, a loop-friendly zoom preset that eases in and back out so rendered preview loops do not jump at the seam.
- Tuned `orbit` with extra overscan and softer depth displacement to reduce corner exposure and tile-edge trails at higher strength values.

## 2026-05-30

- Responded to first external feedback by making the empty preview `+` open the image picker.
- Added three loop-friendly motion presets: `drift`, `push_pull`, and `vertical_float`.
- Kept the browser renderer, internal API renderer, optional DepthFlow adapter, benchmark gallery, and local UI preset lists in sync.
