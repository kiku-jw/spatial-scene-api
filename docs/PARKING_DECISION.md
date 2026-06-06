# Parking Decision

## Decision

Park Spatial Scene / Parallax Video API as a public prototype and portfolio artifact.

Do not continue toward a standalone SaaS unless there is paid validation from content factories, automation users, or creators with recurring batch volume.

## 2026-06-06 Update

The standalone SaaS/API remains parked. The browser-only version is still worth keeping alive as a lightweight validation asset because it has near-zero infrastructure cost and demonstrates the local-first positioning clearly.

Current stage:

- Public prototype and GitHub Pages demo.
- Browser-only local renderer, not production SaaS.
- Soft `Pro Export` fake door added on a branch to measure intent before building payments.
- No real paywall, accounts, billing, GPU backend, or cloud renderer.

Current goal:

- Validate whether users want a better local image-to-parallax export workflow enough to click `Pro`, leave contact info, or ask for batch/high-quality export.
- Do not optimize for generic SEO or platform buildout before demand proof.
- Move to `kikuai.dev/tools/spatial-scene` only after there is measurable intent.

Recommended next decision:

- Add a privacy-safe event collector and waitlist destination.
- Run a two-week demand sprint.
- Continue only if the fake door produces qualified Pro intent; otherwise keep this as a portfolio/demo artifact.

## Why

- The technical prototype works, including FastAPI endpoints, local UI, deterministic fallback rendering, optional Depth Anything depth estimation, and optional external DepthFlow rendering.
- The product wedge is not strong enough on its own. A parallax-only API is more likely a feature inside a larger video automation stack than a durable standalone business.
- The best local renderer tested is DepthFlow, but DepthFlow and ShaderFlow are AGPL-3.0. That is useful for research and local experimentation, but risky for a closed commercial API.
- A production version would need a clean-room renderer, a permissive depth model, and validated unit economics before cloud GPU investment.

## Keep

- Keep the repo public as a build artifact.
- Keep the GitHub Pages browser demo as a zero-infrastructure public artifact.
- Keep the internal renderer as a deterministic baseline.
- Keep DepthFlow integration isolated as an optional external spike, not bundled core code.
- Keep the research notes because they explain why simple zoom/warp was not enough.

## Reopen Criteria

Reopen only if at least one of these happens:

- A paid pilot wants batch conversion of image sets into short vertical videos.
- The workflow expands beyond parallax into a broader ready-to-post video automation system.
- A permissive renderer path reaches acceptable visual quality.
- Unit economics support a clear margin after rendering cost.

## Current Best Next Step

Use this project as a portfolio case, reference implementation, and browser-only demo. Do not rent production GPU infrastructure for it without demand proof.

If continuing validation, the next best step is not renderer work. It is measurement: connect a simple event endpoint, send qualified traffic, and evaluate whether users ask for Pro export features.
