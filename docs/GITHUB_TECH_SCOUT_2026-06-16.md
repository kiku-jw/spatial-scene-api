# GitHub Tech Scout: Spatial Scene Quality

Date: 2026-06-16

## Scope

Find GitHub / OSS components that can strengthen Spatial Scene without changing the product promise:

- browser-local first;
- no generative image-to-video;
- no server upload requirement;
- deterministic image/depth/warp/export pipeline;
- commercial-friendly licensing preferred.

## Short Verdict

The strongest near-term upgrade is not a bigger SaaS backend. It is a better browser renderer:

1. Keep `@huggingface/transformers` with `onnx-community/depth-anything-v2-small` as the default ML depth path.
2. Add an optional full-precision / quality depth mode only from commercially safe model variants.
3. Replace the tiled 2D canvas warp with a Three.js/WebGL subdivided displacement mesh.
4. Add a WebCodecs + Mediabunny export spike before ffmpeg.wasm.
5. Add pixel-level visual regression checks for edge trails, black borders, and block artifacts.

Avoid copying full 3D-photo / 3D-Ken-Burns repos into the product. They are useful references, but often heavy, CUDA/Python-centric, stale, or license-contaminated by non-commercial dependencies.

## Candidate Matrix

| Candidate | Type | Signals | License | Fit | Limits | Link |
|---|---|---:|---|---|---|---|
| `onnx-community/depth-anything-v2-small` | Browser-ready ONNX depth model | HF downloads about 29k; q4/quantized about 26 MB; full ONNX about 94.5 MB | Apache-2.0 | Best current default; works with Transformers.js; commercial-friendly | Small model still produces imperfect object boundaries | https://huggingface.co/onnx-community/depth-anything-v2-small |
| `onnx-community/depth-anything-v2-base` / `large` | Larger ONNX depth models | Base q4 about 97.5 MB; large q4 about 303 MB | CC-BY-NC-4.0 | Better quality candidate in theory | Non-commercial license: do not use for product | https://huggingface.co/onnx-community/depth-anything-v2-base |
| `onnx-community/depth-anything-v3-small` | New ONNX depth candidate | Apache-2.0; about 100 MB split ONNX data; low current usage | Apache-2.0 | Worth a spike as optional quality depth | Not clearly tagged for Transformers.js; may need raw ONNX Runtime path | https://huggingface.co/onnx-community/depth-anything-v3-small |
| `DepthAnything/Depth-Anything-V2` | Official depth repo | about 8.3k stars; active; NeurIPS 2024 | Apache-2.0 | Reference for depth behavior and model family | Python/reference repo, not browser integration itself | https://github.com/DepthAnything/Depth-Anything-V2 |
| `ByteDance-Seed/Depth-Anything-3` | Official V3 depth repo | about 5.6k stars; active | Apache-2.0 | Future reference for better depth | Current wrappers are mostly TensorRT/ROS/DeepStream, not browser-local | https://github.com/ByteDance-Seed/Depth-Anything-3 |
| `huggingface/transformers.js` | Browser ML runtime | about 16.1k stars; active; npm `4.2.0` | Apache-2.0 | Keep using it for browser-local ML depth and caching | WebGPU support varies by browser; model compatibility must be tested | https://github.com/huggingface/transformers.js |
| `mrdoob/three.js` | WebGL/WebGPU 3D renderer | about 113k stars; npm `0.184.0` | MIT | Best renderer upgrade path: depth texture + subdivided mesh + GPU interpolation | Adds dependency and needs careful export-canvas handling | https://github.com/mrdoob/three.js |
| `Vanilagy/mediabunny` | Browser media encode/mux toolkit | about 6.5k stars; npm `1.48.0` | MPL-2.0 | Better export path with WebCodecs/MP4 muxing | Browser support and MPL compliance need review | https://github.com/Vanilagy/mediabunny |
| `Vanilagy/mp4-muxer` | MP4 muxer | about 600 stars; npm deprecated in favor of Mediabunny | MIT | Could be simpler than Mediabunny | Deprecated, so avoid new integration unless Mediabunny fails | https://github.com/Vanilagy/mp4-muxer |
| `ffmpegwasm/ffmpeg.wasm` | Browser ffmpeg | about 17.6k stars; wrapper MIT | Wrapper MIT; `@ffmpeg/core` GPL-2.0-or-later; core about 65 MB | Powerful export/transcode fallback | Heavy, slower, GPL core implications; not first choice | https://github.com/ffmpegwasm/ffmpeg.wasm |
| `mapbox/pixelmatch` | Visual diff test utility | about 6.8k stars; npm `7.2.0` | ISC | Cheap regression checks for seams, black borders, block artifacts | Does not measure perceived 3D quality alone | https://github.com/mapbox/pixelmatch |
| `xuebinqin/U-2-Net` | Salient object segmentation | about 9.8k stars | Apache-2.0 | Reference for object/saliency mask refinement | Browser integration/model size not solved | https://github.com/xuebinqin/U-2-Net |
| `ZHKKKe/MODNet` | Portrait matting | about 4.3k stars | Apache-2.0 | Useful only for portrait-specific foreground masks | Not general image segmentation | https://github.com/ZHKKKe/MODNet |
| `danielgatis/rembg` | Background removal toolkit | about 23.3k stars | MIT | Good reference for masks and model choices | Python/tooling path, not browser-local by default | https://github.com/danielgatis/rembg |
| `facebookresearch/segment-anything` | Segmentation model | about 54k stars | Apache-2.0 | Strong manual/object mask reference | Too heavy and not automatic enough for one-click UX | https://github.com/facebookresearch/segment-anything |
| `advimman/lama` | Inpainting | about 10k stars | Apache-2.0 | Could fill disoccluded background in a future non-browser or optional heavy path | Inpainting changes pixels and can drift from "no mutations"; not near-term browser MVP | https://github.com/advimman/lama |
| `vt-vl-lab/3d-photo-inpainting` | Full 3D-photo / LDI reference | about 7.1k stars | Repo has MIT pieces, but bundled EdgeConnect is CC-BY-NC | Best conceptual reference for layered depth/inpainting | Do not copy as-is into product due non-commercial dependency and heavy Python path | https://github.com/vt-vl-lab/3d-photo-inpainting |
| `sniklaus/3d-ken-burns` | Full 3D Ken Burns implementation | about 1.6k stars | CC-BY-NC-SA-4.0 | Strong algorithm reference | Not product-compatible as-is; CUDA/PyTorch heavy | https://github.com/sniklaus/3d-ken-burns |
| `pierlj/ken-burns-effect` | 3D Ken Burns variant | about 55 stars | MIT | Reference for crop/camera/inpaint architecture | Stale, PyTorch/CUDA path; not browser MVP | https://github.com/pierlj/ken-burns-effect |

## Evidence

- GitHub repo metadata checked with `gh repo view` / `gh search repos` on 2026-06-16.
- NPM packages checked with `npm view` on 2026-06-16:
  - `@huggingface/transformers`: `4.2.0`, Apache-2.0, unpacked about 9.5 MB.
  - `three`: `0.184.0`, MIT, unpacked about 37 MB.
  - `mediabunny`: `1.48.0`, MPL-2.0, unpacked about 9.8 MB.
  - `@ffmpeg/ffmpeg`: `0.12.15`, MIT wrapper.
  - `@ffmpeg/core`: `0.12.10`, GPL-2.0-or-later, unpacked about 65 MB.
  - `mp4-muxer`: `5.2.2`, MIT, deprecated in favor of Mediabunny.
  - `pixelmatch`: `7.2.0`, ISC.
- Hugging Face model metadata checked via HF API on 2026-06-16:
  - `onnx-community/depth-anything-v2-small`: Apache-2.0; q4/quantized around 26 MB; full ONNX around 94.5 MB.
  - `onnx-community/depth-anything-v2-base`: CC-BY-NC-4.0; q4 around 97.5 MB.
  - `onnx-community/depth-anything-v2-large`: CC-BY-NC-4.0; q4 around 303 MB.
  - `onnx-community/depth-anything-v3-small`: Apache-2.0; ONNX data around 99.9 MB.

## Recommendations

### Try first

1. WebGL mesh renderer with Three.js.
   - Replace tiled 2D canvas warping with a dense plane mesh.
   - Use source image as a texture and depth map as a displacement texture.
   - Render to the same export canvas dimensions and downscale only for preview.
   - This directly attacks visible block/chunk artifacts and edge tearing.

2. Depth quality selector with only safe models.
   - Default: `depth-anything-v2-small` quantized, about 26 MB.
   - Optional quality mode: `depth-anything-v2-small` full ONNX, about 94.5 MB, if Transformers.js supports it cleanly.
   - Experimental research mode: `depth-anything-v3-small`, about 100 MB, behind a feature flag.
   - Do not use V2 base/large in product because HF model cards show CC-BY-NC-4.0.

3. WebCodecs export spike with Mediabunny.
   - Goal: compare output quality and file size against current MediaRecorder.
   - Keep MediaRecorder fallback.
   - Avoid ffmpeg.wasm unless WebCodecs path fails, because ffmpeg core is heavy and GPL.

4. Visual QA harness with Pixelmatch.
   - Render 5-10 known frames for each preset.
   - Fail on black borders, blank frames, obvious seam deltas, and excessive block artifacts.
   - Keep this as an internal regression test, not a user-facing quality metric.

### Avoid for now

- `imgly/background-removal-js`: technically relevant but AGPL-3.0, not a good fit for our product code.
- `sniklaus/3d-ken-burns`: non-commercial share-alike license, heavy CUDA/PyTorch path.
- `vt-vl-lab/3d-photo-inpainting`: good reference, but its license stack includes CC-BY-NC EdgeConnect.
- `ffmpeg.wasm` as default export: too heavy and GPL core; consider only as explicit optional export worker later.
- SAM as default object layer system: Apache-2.0 but too heavy and not one-click enough.

### Build ourselves instead

Build the Spatial Scene engine boundary ourselves:

- `DepthProvider`: current fast/ML depth plus optional model variants.
- `MotionPlanner`: deterministic preset camera paths and loop-safe easing.
- `Renderer`: new WebGL mesh path plus current canvas fallback.
- `Exporter`: MediaRecorder fallback plus WebCodecs/Mediabunny experiment.
- `QualityGate`: pixelmatch-based smoke/regression checks.

This preserves the product promise and avoids importing research-code complexity into the user-facing tool.

## Suggested Next Spike

One focused spike should be enough:

- Add a hidden `renderer=webgl` path.
- Implement a Three.js plane mesh with 160x284 or adaptive subdivisions for portrait 1080x1920.
- Feed the existing depth map into vertex displacement.
- Render 5-second `zoom_in_out` and `orbit` samples.
- Compare against current canvas renderer using file size, visual inspection, and pixelmatch edge/border checks.

Pass condition:

- visibly less block/tile artifacting;
- no new black borders;
- no worse render time than about 1.5x current renderer on Nick's machine;
- no semantic image mutation.
