# Spatial Scene Validation PRD

## Overview

- **Product Name:** KikuAI Spatial Scene
- **Author:** Nick / Codex
- **Date:** 2026-06-11
- **Status:** Draft
- **MVP deadline:** 7-day validation sprint after tracking and quality guardrails are live

## 1. Problem Statement

We believe performance marketers, agency creatives, DTC/ecommerce teams, and some AI-image creators need a fast way to turn still images into short social-ready motion assets without uploading source images and without generative image-to-video mutations.

Current evidence:

- The broad image-to-video / parallax space is crowded with substitutes such as CapCut, Canva, Runway, Pika, Luma, Immersity, mobile photo-animation apps, and After Effects workflows.
- The strongest buyer-fit use case is not casual image animation. It is repeated commercial motion-asset production from existing product, ad, or AI-image assets.
- The differentiator is not generic AI video. It is source-faithful local motion: exact image in, conservative camera motion out.
- Browser-local depth is technically feasible with `Depth Anything V2 Small`, `Transformers.js`, ONNX Runtime Web, WebGPU first, and WASM fallback.
- The biggest product risk is visual quality. Edge tearing, holes, object trails, low-quality export, and over-strong orbit motion can make the output unusable.

This PRD does not assume Spatial Scene is ready to become a standalone SaaS. It defines the smallest validation product needed to decide whether to continue beyond a public browser-local prototype.

## 2. Target Users

### Pilot Segment

Primary:

- performance marketers;
- agency creatives;
- DTC/ecommerce teams;
- Shopify / marketplace operators creating product or ad motion assets from still images.

Secondary:

- AI-image creators who need subtle motion without changing faces, characters, products, text, or art style.

### NOT for MVP

- generic short-form creators who only want novelty effects;
- enterprise video teams requiring SOC2, seats, SSO, audit logs, or procurement review;
- users needing text-to-video, lip sync, avatars, talking heads, or full video editing;
- users needing server-side API throughput or guaranteed cloud rendering;
- users expecting strong cinematic motion for any image, regardless of input suitability.

## 3. Proposed Solution

Create a browser-local Spatial Scene tool on KikuAI that lets a user drop one image, preview conservative source-faithful motion, and export or express intent for a clean 1080p result.

The MVP should test three questions:

1. Can the browser-local renderer produce output users consider publishable enough?
2. Do buyer-fit users care about no-upload / no-mutation enough to prefer it over easy substitutes?
3. Will users click or pay for a clean export / batch workflow before we build a real SaaS layer?

The tool should:

- keep source images local in the browser;
- avoid generative image-to-video;
- use deterministic camera-motion presets;
- use local ML depth when available and degrade honestly when unavailable;
- clamp risky motion instead of producing obvious artifacts;
- show clear export / Pro intent surfaces without blocking basic validation.

## 4. Scope

| IN (Validation MVP) | OUT (Post-Validation) |
|---|---|
| Browser-local single-image upload | Accounts |
| Preview in the same drop/result stage | Teams / workspaces |
| Conservative motion presets | Stripe/Paddle subscription platform |
| Default 30 FPS | Enterprise procurement / SOC2 |
| 9:16, 1:1, and 16:9 export targets | Cloud GPU render backend |
| Fast/default local depth path with fallback | Public API throughput |
| Device capability / hardware requirement panel | Webhooks |
| Clear local privacy copy | Zapier/Make/n8n integrations |
| Quality guardrails and strength clamping | Batch processing at scale |
| Image suitability warnings | Desktop app |
| Preview/export parity improvements | Mobile native app |
| Fake-door or simple checkout CTA for clean export | Template marketplace |
| Privacy-safe event tracking | Full video editor |
| Two buyer-intent landing pages | Text-to-video |
| Before/after sample gallery | Generative inpainting that changes content |

## 5. P0 Requirements

- [ ] The first screen shall show a compact drop/result stage before advanced settings.
- [ ] The tool shall keep image processing local in the browser during validation.
- [ ] The tool shall not use generative image-to-video or rewrite image content.
- [ ] The default motion shall be conservative enough to avoid obvious edge tearing on common inputs.
- [ ] The renderer shall clamp or warn on risky high-strength motion, especially orbit/circle-style movement.
- [ ] The UI shall explain when local ML depth is available, slow, unavailable, or falling back.
- [ ] The output path shall preserve visual quality better than the current low-quality/chunky render path.
- [ ] The tool shall provide a clear export or Pro intent CTA tied to a clean finished asset.
- [ ] The app shall track privacy-safe funnel events without sending image bytes, video bytes, filenames, local paths, or prompt text.
- [ ] The product page shall clearly position the tool as no-upload, source-faithful motion export.
- [ ] The validation sprint shall have explicit kill criteria before additional SaaS buildout.

## 6. Success Metrics

Measure only buyer-fit activity, not generic page views.

| Metric | Target | How Measured |
|---|---:|---|
| Buyer-fit visits | 100+ | Referrer/source + page intent + manual review |
| Render starts | 30+ | Privacy-safe `render_started` event |
| Successful exports/downloads | 10+ | Privacy-safe `export_clicked` / `render_completed` event |
| Pro / clean export clicks | 5+ | `pro_clicked` or checkout-link event |
| Strong payment signal | 3+ | checkout attempts, purchases, or direct requests |
| Repeat intent | 2+ users | second export, batch request, or follow-up message |
| Quality blocker rate | below 50% of feedback | manual feedback classification |

Kill or park the active push if:

- fewer than 10 exports happen after 100 buyer-fit visits;
- fewer than 3 checkout attempts or strong Pro clicks happen after qualified traffic;
- users mostly praise the demo but do not ask for clean export, batch, no watermark, or higher quality;
- feedback clusters around core renderer artifacts rather than packaging or workflow limits;
- the strongest feedback is that CapCut, Canva, or Immersity already does enough.

## 7. Quality Requirements

Spatial Scene should promise:

> exact image in, conservative camera motion out.

It should not promise:

> any image can become cinematic.

Safe defaults:

- default preset should favor vertical float, center zoom, or subtle drift;
- orbit/circle should be treated as high-risk and clamped;
- default strength should be low-to-medium;
- output should preserve source resolution where practical and avoid unnecessary resampling;
- preview should not hide artifacts that appear in export.

A render is acceptable only if:

- objects, faces, text, and product identity remain unchanged;
- object edges do not visibly tear, trail, or reveal holes at native playback size;
- static regions do not shimmer;
- motion reads as camera movement, not image melting;
- exported video looks close to the preview.

## 8. Browser ML Policy

Use a tiered depth strategy:

| Tier | Model / dtype | Runtime | Input budget | Use |
|---|---|---|---|---|
| Fast | `q4f16` or `q4` | WebGPU first, WASM fallback | 384-448 short side | fast preview / weak devices |
| Default | `q8` or `fp16` | WebGPU preferred | 512 short side | normal local export |
| Pro | `fp16`; `fp32` only on strong desktops | WebGPU only | 640-768 short side | explicit high-quality export |

Rules:

- probe device capability before promising quality;
- request persistent cache only after explicit user intent;
- separate low-resolution preview from higher-quality export;
- never run frame-by-frame depth on video in the browser;
- do not use non-commercial depth models in the commercial path;
- do not hide fallback behavior from the user.

## 9. First-Money Experiment

Do not start with subscriptions.

Ranked validation offers:

1. **Clean HD export unlock** - $9-$12 one-time per scene.
2. **Batch export pack** - $29-$49 one-time.
3. **Pro quality mode** - $19-$29 one-time add-on.

Free should include:

- upload;
- preview;
- basic local render;
- no account requirement during validation.

The paid moment should be tied to a finished asset:

- clean 1080p export;
- watermark-free export;
- commercial-use clarity;
- batch convenience.

## 10. Distribution Requirements

The validation sprint should start with buyer-intent pages, not broad SEO.

Required pages:

- `CapCut 3D Zoom alternative`
- `Product photo to video ad`

Useful supporting assets:

- before/after sample gallery;
- browser-local / no-upload proof page;
- motion recipe gallery;
- short comparison clips.

Primary query clusters:

- `CapCut 3D Zoom alternative`
- `product photo to video ad`
- `Shopify product photo to video`
- `product video ads from still images`
- `no upload image to video`
- `browser local image to video`
- `image to video without changing face`

## 11. Open Questions

- Which analytics/event backend should be used first?
- Should the first payment test use a fake-door form, Stripe Payment Link, Gumroad, Lemon Squeezy, or manual contact?
- Should the first clean export offer show $9 or $12?
- What exact watermark/preview limitation is acceptable without making the free tool feel deceptive?
- Which sample images best represent buyer-fit use cases: ecommerce product, ad creative, AI art, or mixed gallery?
- Should the public product name keep `Spatial Scene`, or shift to a less Apple-adjacent phrase such as `KikuAI Image Motion`?

## 12. Decision

Proceed only with a narrow 7-day validation sprint.

Do not build accounts, billing infrastructure, backend rendering, desktop/mobile apps, or API throughput until qualified users show export/payment intent.

If the sprint passes, the next product step is batch export and better browser-local quality tiers. If it fails, keep Spatial Scene as a public browser-local portfolio artifact.
