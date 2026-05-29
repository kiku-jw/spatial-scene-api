# Spatial Scene MVP Plan

## Goal

Build a local web/API MVP that converts one static image into a deterministic 9:16 MP4 with subtle parallax motion.

## Scope

- FastAPI backend.
- Minimal static web UI.
- Deterministic fallback depth map.
- Four presets: `orbit`, `zoom_in`, `zoom_out`, `zoom_in_out`.
- Local `uploads/` and `outputs/` storage.
- README with run and API examples.

## Acceptance

- Server starts locally.
- UI upload returns an MP4 preview/download link.
- `/api/render` and `/v1/parallax` both return JSON with `job_id`, `status`, and output URLs.
- All presets generate non-empty MP4 files with roughly requested duration.
- No paid or generative video API is required.

## Verification Commands

```bash
python -m compileall app
uvicorn app.main:app --host 127.0.0.1 --port 8000
curl -X POST "http://127.0.0.1:8000/api/render" -F "file=@samples/sample_scene.png" -F "preset=orbit"
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 outputs/<file>.mp4
```
