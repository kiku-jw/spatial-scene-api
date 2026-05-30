# Feedback Motion Pack Design

## Goal

Respond to the first external feedback round with one focused browser-demo update:

- make the empty preview `+` an intuitive image-upload trigger;
- add three visibly different, loop-friendly motion presets;
- keep the existing deterministic, local-only rendering model;
- preserve image quality by keeping motion subtle enough for the current mesh renderer.

## User Experience

Before an image is loaded, the full empty preview area is a file-picker button and still accepts drag-and-drop. Once an image is loaded, clicking the preview does not reopen the picker accidentally.

The preset menu gains:

- `drift`: slow diagonal lateral motion with restrained depth separation;
- `push_pull`: a loop-friendly dolly-in/dolly-out motion with stronger depth separation;
- `vertical_float`: vertical rise-and-fall with a small horizontal sway.

Existing `orbit` and `zoom_in_out` remain available. Their browser settings stay within the artifact-resistant range established by the orbit cleanup.

## Architecture

The browser demo adds motion formulas to `getMotion()` in `docs/index.html`. The backend renderer adds matching deterministic formulas to `_source_coordinates()` in `app/render.py`. The optional external DepthFlow adapter maps each new preset onto its closest supported composition of built-in motions.

No new dependencies, models, queues, or UI panels are added.

## Verification

- Static browser tests confirm clickable empty upload state and menu presence.
- Backend motion tests confirm all loop-friendly presets return identical source coordinates at the start and end of a cycle while changing at the midpoint.
- DepthFlow command tests confirm each preset maps to a supported external command.
- Browser smoke test confirms clicking the empty preview opens the file chooser and a rendered preset produces a looping downloadable MP4.
