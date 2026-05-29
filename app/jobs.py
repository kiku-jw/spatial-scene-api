from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class JobRecord:
    job_id: str
    status: str
    preset: str
    duration_seconds: float
    fps: int
    aspect_ratio: str
    strength: str
    renderer: str = "internal"
    depth_provider: str = "fallback"
    input_filename: str | None = None
    output_filename: str | None = None
    error: str | None = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "job_id": self.job_id,
            "status": self.status,
            "preset": self.preset,
            "duration_seconds": self.duration_seconds,
            "fps": self.fps,
            "aspect_ratio": self.aspect_ratio,
            "strength": self.strength,
            "renderer": self.renderer,
            "depth_provider": self.depth_provider,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.input_filename:
            payload["input_filename"] = self.input_filename
        if self.output_filename:
            payload["output_filename"] = self.output_filename
            payload["download_url"] = f"/outputs/{self.output_filename}"
            payload["preview_url"] = f"/outputs/{self.output_filename}"
        if self.error:
            payload["error"] = self.error
        return payload


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = Lock()

    def create(
        self,
        job_id: str,
        preset: str,
        duration_seconds: float,
        fps: int,
        aspect_ratio: str,
        strength: str,
        renderer: str = "internal",
        depth_provider: str = "fallback",
    ) -> JobRecord:
        record = JobRecord(
            job_id=job_id,
            status="queued",
            preset=preset,
            duration_seconds=duration_seconds,
            fps=fps,
            aspect_ratio=aspect_ratio,
            strength=strength,
            renderer=renderer,
            depth_provider=depth_provider,
        )
        with self._lock:
            self._jobs[job_id] = record
        return record

    def update(self, job_id: str, **changes: Any) -> JobRecord:
        with self._lock:
            record = self._jobs[job_id]
            for key, value in changes.items():
                setattr(record, key, value)
            record.updated_at = _now()
            return record

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)
