# Parking Decision

## Decision

Park Spatial Scene / Parallax Video API as a public prototype and portfolio artifact.

Do not continue toward a standalone SaaS unless there is paid validation from content factories, automation users, or creators with recurring batch volume.

## Why

- The technical prototype works, including FastAPI endpoints, local UI, deterministic fallback rendering, optional Depth Anything depth estimation, and optional external DepthFlow rendering.
- The product wedge is not strong enough on its own. A parallax-only API is more likely a feature inside a larger video automation stack than a durable standalone business.
- The best local renderer tested is DepthFlow, but DepthFlow and ShaderFlow are AGPL-3.0. That is useful for research and local experimentation, but risky for a closed commercial API.
- A production version would need a clean-room renderer, a permissive depth model, and validated unit economics before cloud GPU investment.

## Keep

- Keep the repo public as a build artifact.
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

Use this project as a portfolio case and reference implementation. Do not rent production GPU infrastructure for it without demand proof.
