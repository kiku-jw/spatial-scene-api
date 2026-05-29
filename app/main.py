from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.depth import DepthProviderUnavailable
from app.depthflow_external import (
    DepthFlowRenderError,
    DepthFlowUnavailable,
    render_depthflow_video,
)
from app.jobs import JobStore
from app.render import RenderError, build_settings, render_parallax_video


ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "app" / "static"
UPLOAD_DIR = ROOT_DIR / "uploads"
OUTPUT_DIR = ROOT_DIR / "outputs"
SAMPLES_DIR = ROOT_DIR / "samples"
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_RENDERERS = {"internal", "depthflow"}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Spatial Scene / Parallax Video API", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

job_store = JobStore()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/render")
async def api_render(
    file: UploadFile = File(...),
    preset: str = Form("orbit"),
    duration_seconds: float = Form(10.0),
    fps: int = Form(30),
    aspect_ratio: str = Form("9:16"),
    strength: str = Form("safe"),
    renderer: str = Form("internal"),
    depth_provider: str = Form("fallback"),
) -> dict[str, object]:
    return await _render_request(
        file=file,
        image_url=None,
        preset=preset,
        duration_seconds=duration_seconds,
        fps=fps,
        aspect_ratio=aspect_ratio,
        strength=strength,
        renderer=renderer,
        depth_provider=depth_provider,
    )


@app.post("/v1/parallax")
async def v1_parallax(
    file: UploadFile | None = File(None),
    image_url: str | None = Form(None),
    preset: str = Form("orbit"),
    duration_seconds: float = Form(10.0),
    fps: int = Form(30),
    aspect_ratio: str = Form("9:16"),
    strength: str = Form("safe"),
    renderer: str = Form("internal"),
    depth_provider: str = Form("fallback"),
) -> dict[str, object]:
    return await _render_request(
        file=file,
        image_url=image_url,
        preset=preset,
        duration_seconds=duration_seconds,
        fps=fps,
        aspect_ratio=aspect_ratio,
        strength=strength,
        renderer=renderer,
        depth_provider=depth_provider,
    )


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, object]:
    record = job_store.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return record.to_dict()


async def _render_request(
    file: UploadFile | None,
    image_url: str | None,
    preset: str,
    duration_seconds: float,
    fps: int,
    aspect_ratio: str,
    strength: str,
    renderer: str,
    depth_provider: str,
) -> dict[str, object]:
    try:
        normalized_renderer = _normalize_renderer(renderer)
        settings = build_settings(
            preset=preset,
            duration_seconds=duration_seconds,
            fps=fps,
            aspect_ratio=aspect_ratio,
            strength=strength,
            depth_provider=depth_provider,
        )
    except ValueError:
        error = sys.exception()
        raise HTTPException(status_code=400, detail=str(error))

    job_id = uuid4().hex
    record = job_store.create(
        job_id=job_id,
        preset=settings.preset,
        duration_seconds=settings.duration_seconds,
        fps=settings.fps,
        aspect_ratio=settings.aspect_ratio,
        strength=settings.strength,
        renderer=normalized_renderer,
        depth_provider=settings.depth_provider,
    )

    try:
        input_path = await _save_input(job_id, file, image_url)
        output_filename = f"{job_id}.mp4"
        output_path = OUTPUT_DIR / output_filename
        job_store.update(
            record.job_id,
            status="rendering",
            input_filename=input_path.name,
        )
        if normalized_renderer == "depthflow":
            render_depthflow_video(input_path, output_path, settings)
        else:
            render_parallax_video(input_path, output_path, settings)
        record = job_store.update(
            record.job_id,
            status="done",
            output_filename=output_filename,
        )
        return record.to_dict()
    except HTTPException:
        job_store.update(record.job_id, status="failed", error="Request failed")
        raise
    except RenderError:
        error = sys.exception()
        job_store.update(record.job_id, status="failed", error=str(error))
        raise HTTPException(status_code=422, detail=str(error))
    except DepthProviderUnavailable:
        error = sys.exception()
        job_store.update(record.job_id, status="failed", error=str(error))
        raise HTTPException(status_code=503, detail=str(error))
    except DepthFlowUnavailable:
        error = sys.exception()
        job_store.update(record.job_id, status="failed", error=str(error))
        raise HTTPException(status_code=503, detail=str(error))
    except DepthFlowRenderError:
        error = sys.exception()
        job_store.update(record.job_id, status="failed", error=str(error))
        raise HTTPException(status_code=422, detail=str(error))
    except Exception:
        error = sys.exception()
        job_store.update(record.job_id, status="failed", error=str(error))
        raise HTTPException(status_code=500, detail=str(error))


async def _save_input(
    job_id: str,
    file: UploadFile | None,
    image_url: str | None,
) -> Path:
    if file is not None:
        data = await file.read()
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Image exceeds 25 MB")
        suffix = _suffix_from_name(file.filename or "")
        path = UPLOAD_DIR / f"{job_id}{suffix}"
        path.write_bytes(data)
        return path

    if image_url:
        return _download_image(job_id, image_url)

    raise HTTPException(status_code=400, detail="Provide file or image_url")


def _download_image(job_id: str, image_url: str) -> Path:
    parsed = urlparse(image_url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="image_url must be http or https")

    suffix = _suffix_from_name(parsed.path)
    request = Request(image_url, headers={"User-Agent": "SpatialSceneAPI/0.1"})
    response = urlopen(request, timeout=20)
    try:
        content = response.read(MAX_UPLOAD_BYTES + 1)
    finally:
        response.close()

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds 25 MB")

    path = UPLOAD_DIR / f"{job_id}{suffix}"
    path.write_bytes(content)
    return path


def _suffix_from_name(name: str) -> str:
    suffix = Path(name).suffix.lower()
    if suffix in ALLOWED_SUFFIXES:
        return suffix
    return ".png"


def _normalize_renderer(renderer: str) -> str:
    normalized = renderer.strip().lower() or "internal"
    if normalized in ALLOWED_RENDERERS:
        return normalized
    raise ValueError("renderer must be internal or depthflow")
