# Renderer Research Decision

## Context

The first renderer proves the API and UI path, but it does not meet the spatial-scene quality bar. It mostly zooms, stretches, or warps the centered image. The missing piece is not more motion strength; it is a better scene representation with room for camera movement.

Good spatial photo animation needs:

- monocular depth estimation;
- a pseudo-3D representation such as DIBR, mesh, LDI, or MPI;
- disocclusion handling for newly revealed background;
- restrained camera paths and edge fill;
- no mutation of original primary subjects.

## Research Input

Local deep-research notes were reviewed during the prototype phase. The report compared DIBR, LDI/context-aware inpainting, MPI/mesh approaches, 3D Ken Burns pipelines, DepthFlow, 3D-Photo-Inpainting, Tiefling, and depth models such as Depth Anything and ZoeDepth.

## Decision

Do not keep investing in the current NumPy layered-warp renderer as the main quality path. Keep it as a fallback and API proof.

Run a renderer spike in this order:

1. **DepthFlow** as an external renderer candidate.
   - Best fit for fast, stable, non-generative parallax.
   - Preserves original semantics because it does not synthesize primary image content.
   - Likely still stretches/blends disocclusions, but should do it much better than our CPU warp.
   - Main risks: AGPL-3.0 license and GPU/OpenGL compatibility, especially on Apple Silicon.

2. **MIT/Apache custom path** if DepthFlow is blocked.
   - Use Depth Anything small or ZoeDepth for depth.
   - Build or adapt a mesh/WebGL/Three.js-style renderer with depth dilation and edge padding.
   - This is cleaner for future commercial API use than copying AGPL or non-commercial research code.

3. **3D-Photo-Inpainting / LDI** only as quality reference.
   - Useful for understanding disocclusion fill.
   - Not a default MVP dependency because of old stack, slow runtime, and non-commercial inpainting-model risk.

## Non-Goals For The Next Spike

- Do not add generative image-to-video.
- Do not mutate faces, text, logos, or primary subjects.
- Do not fold AGPL code into this repository.
- Do not rewrite the FastAPI product surface until one renderer produces visibly better videos.

## Spike Success Criteria

- Produce at least one 9:16 MP4 from a representative local image sample.
- Motion reads as spatial: near and far regions separate, not just center stretch.
- No black borders or severe tearing.
- Original subjects stay semantically unchanged.
- Runtime and hardware requirements are documented.
- License risk is explicitly recorded before any integration choice.

## Next Implementation Shape

If DepthFlow works locally, integrate it behind a separate renderer provider:

- `renderer=internal_fallback`
- `renderer=depthflow_external`

The API should preserve the existing endpoints and return the same job schema. DepthFlow should be invoked as a separate process or optional dependency first, not imported as core app code.
