# Spatial Scene Plan

## Current Goal

Validate whether Spatial Scene deserves continued product investment beyond a public browser-local prototype.

The current direction is defined in:

- `docs/PRD.md` - validation PRD.
- `docs/VALIDATION_RESEARCH_SYNTHESIS_2026-06-11.md` - research synthesis and decision memo.
- `docs/PRO_VALIDATION_PLAN.md` - fake-door and event-collection plan.

The old local FastAPI MVP has already been built. It remains useful as a technical artifact and fallback implementation, but it is no longer the main product plan.

## Scope

- Keep rendering browser-local during validation.
- Improve quality guardrails: conservative defaults, motion clamping, suitability warnings, and better export fidelity.
- Use local ML depth only with honest device detection and fallback.
- Add or wire privacy-safe events for render/export/Pro intent.
- Test buyer-fit traffic through narrow intent pages:
  - `CapCut 3D Zoom alternative`;
  - `Product photo to video ad`.
- Test a clean export intent offer before building real SaaS infrastructure.

## Acceptance For Next Validation Sprint

- The first screen is a compact drop/result stage.
- Users can render and preview without uploading image bytes to KikuAI.
- The UI clearly explains local depth, fallback, and hardware constraints.
- Conservative motion defaults avoid obvious artifacts on representative samples.
- Export/Pro intent is measurable without collecting image/video payloads.
- Validation has explicit kill criteria before billing, accounts, server render, API throughput, or desktop/mobile work.

## Out Of Scope Until Validation Passes

- Accounts.
- Subscriptions.
- Enterprise security review.
- Cloud GPU rendering.
- Public API throughput.
- Batch processing at scale.
- Desktop or mobile apps.
- Generative image-to-video.
- Generative inpainting that changes source content.

## Decision

Run a narrow validation sprint. If buyer-fit users do not show clean-export or batch intent, keep Spatial Scene parked as a public browser-local portfolio artifact.
