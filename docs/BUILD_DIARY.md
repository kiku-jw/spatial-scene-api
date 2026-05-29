# Build Diary

## Artifact Decision

Spatial Scene / Parallax Video API earned a small public repository artifact, not a launch post.

## Evidence

- Local FastAPI web/API MVP exists.
- `/api/render` and `/v1/parallax` render MP4 outputs.
- The UI supports image upload, preset selection, renderer selection, preview, and download.
- Tests and compile checks passed.
- DepthFlow was validated locally as a higher-quality external renderer.
- Product review concluded the standalone SaaS case is weak without paid validation.

## Privacy Gate

- User-provided art samples, uploads, rendered outputs, local spike environments, and browser logs are excluded from git.
- The public repo keeps synthetic samples, source code, docs, and tests.

## Public Shape

- Public GitHub repository.
- GitHub Pages browser demo where image processing happens on the visitor's device.
- README presents the project as a parked prototype and case study.
- Parking decision is documented in `docs/PARKING_DECISION.md`.

## Status

Public archival completed. Browser demo added as a GitHub Pages artifact.
