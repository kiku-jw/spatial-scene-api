# Spatial Scene Validation Research Synthesis

Date: 2026-06-11

## Summary

Spatial Scene should not be treated as a broad standalone SaaS yet. The strongest surviving direction is a narrow validation wedge:

> Browser-local, source-faithful motion export for product/ad images and AI-generated images where users care about no upload, no generative drift, and repeatable short-form output.

The project remains a validation asset until real buyer-fit users show export intent or payment intent. The current best next move is not a full SaaS buildout. It is a short proof sprint around quality, buyer-fit traffic, and clean-export intent.

## Evidence

- The market already has strong substitutes:
  - CapCut and TikTok-style 3D zoom/photo animation flows.
  - Canva photo animation and image-to-video tools.
  - Runway, Pika, and Luma for generative image-to-video.
  - Immersity for 2D-to-3D / parallax conversion and API use.
  - Motionleap, VIMAGE, and other mobile photo animation tools.
  - After Effects and manual parallax workflows for pro users.
- The clearest buyer-fit use case is not casual image animation. It is repeated commercial motion-asset production:
  - performance marketers;
  - agency creatives;
  - DTC / ecommerce teams;
  - product-photo-to-video workflows;
  - secondarily, AI-image creators who need motion without changing character, face, product, text, or style.
- Competitors already cover much of the broad creator workflow. Therefore `No AI mutations` is useful, but not a moat by itself.
- Browser-local depth is technically feasible with a tiered runtime:
  - `Depth Anything V2 Small`;
  - `Transformers.js` / ONNX Runtime Web;
  - WebGPU first;
  - WASM fallback;
  - browser cache/persistent storage when available.
- License constraints are material:
  - `Depth Anything V2 Small` is the safest current model candidate because it is Apache-2.0.
  - Larger Depth Anything V2 variants are non-commercial.
  - DepthPro is not suitable for product integration under its current model license.
  - DepthFlow and parallax-maker are useful references, but AGPL-3.0 makes them risky as commercial product dependencies.
  - 3D Ken Burns and similar research repos are useful references but are non-commercial.

## Inference

The product should be tested as a focused utility, not as a platform:

- Promise: exact image in, conservative camera motion out.
- Do not promise: any image can become cinematic.
- Default product posture: local, deterministic, source-faithful, export-focused.
- First buyer hypothesis: performance marketers / agency creatives / DTC teams that need ad-ready motion assets from existing images.
- Second buyer hypothesis: AI-image creators who need subtle motion without generative face/object/text drift.
- Weak buyer hypothesis: generic short-form creators. They already have cheap, familiar tools and low switching urgency.

## Quality Rulebook

### Safe Defaults

- Default preset: `vertical_float` or similarly conservative motion.
- Default strength: low-to-medium.
- Default FPS: 30.
- Default export quality: preserve source resolution where practical; avoid unnecessary resampling.
- Keep `orbit` conservative because it reveals hidden background and causes the worst edge artifacts.

### Preset Risk

- Lowest risk: vertical float, center zoom, subtle drift.
- Medium risk: push-pull / zoom in-out.
- Highest risk: orbit / circle / perspective.

### Input Suitability

Best candidates:

- layered landscapes;
- interiors with clear foreground, midground, and background;
- product hero shots with clean separation;
- portraits with uncluttered backgrounds.

Risky candidates:

- dense text, logos, UI, posters;
- reflective, transparent, glossy, or glass surfaces;
- thin structures such as hair, fingers, fences, foliage, wires;
- low-resolution or compressed images;
- important subjects clipped near frame edges.

### Acceptance Bar

A render passes only if:

- objects, faces, text, and product identity remain unchanged;
- object edges do not tear, trail, or leave visible holes at native playback size;
- static areas do not shimmer;
- the result reads as camera motion, not image melting;
- preview and exported video match closely enough that download is not a surprise.

## Browser ML Shipping Policy

### Runtime Tiers

| Tier | Model / dtype | Runtime | Input budget | Use |
|---|---|---|---|---|
| Fast | `q4f16` or `q4` | WebGPU first, WASM fallback | 384-448 short side | fast preview / weak devices |
| Default | `q8` or `fp16` | WebGPU preferred | 512 short side | normal local export |
| Pro | `fp16`; `fp32` only on strong desktops | WebGPU only | 640-768 short side | explicit high-quality export |

### UX Rules

- Probe device capability before promising quality.
- Cache the model after explicit user intent.
- Separate low-resolution preview from higher-quality export.
- Never run frame-by-frame depth for video in the browser.
- If local GPU is unavailable or unstable, degrade honestly rather than hiding it.

Suggested copy:

- `Checking whether this device can run depth locally.`
- `This runs locally in your browser. Your image stays on this device.`
- `This device can export locally, but real-time preview would be too slow.`
- `Large camera moves can reveal uncovered areas. We will keep motion subtle to preserve the original image.`

## First-Money Hypothesis

Do not start with subscriptions.

Ranked offers:

1. Clean HD export unlock: $9-$12 one-time per scene.
2. Batch export pack: $29-$49 one-time.
3. Pro quality mode: $19-$29 one-time add-on.

Free should include:

- upload;
- preview;
- basic local render;
- at least one low-friction test path;
- no account requirement during validation.

The paid moment should be tied to a finished asset:

- clean 1080p export;
- watermark-free export;
- commercial-use clarity;
- batch convenience.

## Distribution Test

Do not optimize broad SEO first. Use buyer-intent pages and direct sample-request paths.

Priority query clusters:

- `CapCut 3D Zoom alternative`
- `3D zoom photo effect alternative`
- `image to parallax video`
- `product photo to video ad`
- `Shopify product photo to video`
- `product video ads from still images`
- `no upload image to video`
- `browser local image to video`
- `image to video without changing face`
- `still image into smooth video loop`

Priority pages:

1. `CapCut 3D Zoom alternative`
2. `Product photo to video ad`
3. `Browser-local / no-upload image motion export`
4. Before/after benchmark gallery
5. Motion recipe gallery

Priority communities:

- Shopify / ecommerce communities;
- PPC / performance marketing communities;
- DTC / dropshipping communities;
- CapCut and After Effects users looking for alternatives;
- AI-image creator communities as secondary validation.

## Kill Criteria

Kill or park the active product push if any of these happen:

- After 100 buyer-fit visits, fewer than 30 render attempts.
- After 100 buyer-fit visits, fewer than 10 exports.
- Fewer than 3 checkout attempts or strong Pro clicks after qualified traffic.
- Feedback clusters around core quality artifacts rather than packaging, export limits, or batch workflow.
- Users praise the demo but do not ask for cleaner export, batch, no watermark, or higher quality.
- The strongest feedback is `CapCut/Canva already does enough`.

## Recommended Next Action

Run a 7-day validation sprint before adding real billing or broader platform features.

Minimum sprint:

1. Improve quality guardrails:
   - conservative default preset;
   - motion strength clamping;
   - image suitability warnings;
   - higher-quality export settings;
   - better device-depth messaging.
2. Publish two intent pages:
   - `CapCut 3D Zoom alternative`;
   - `Product photo to video ad`.
3. Add one fake-door or simple checkout CTA:
   - `Unlock clean 1080p export`;
   - price test: $9 or $12.
4. Collect privacy-safe events:
   - render started;
   - render completed;
   - export clicked;
   - Pro clicked;
   - sample request submitted.
5. Evaluate after 7 days using buyer-fit activity, not generic traffic.

## Decision

Keep Spatial Scene active only as a narrow validation experiment. Do not treat it as a standalone SaaS yet.

If the validation sprint produces qualified export/payment intent, move next into batch export and better browser-local quality tiers. If it does not, keep the tool as a public browser-local portfolio artifact.
