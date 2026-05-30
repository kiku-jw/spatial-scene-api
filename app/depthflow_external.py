from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from app.render import RenderSettings


class DepthFlowUnavailable(RuntimeError):
    pass


class DepthFlowRenderError(RuntimeError):
    pass


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_LOCAL_DEPTHFLOW = ROOT_DIR / ".spikes" / "depthflow-venv" / "bin" / "depthflow"


def render_depthflow_video(
    input_path: Path,
    output_path: Path,
    settings: RenderSettings,
) -> Path:
    executable = find_depthflow_binary()
    command = build_depthflow_command(executable, input_path, output_path, settings)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    if sys.platform == "darwin":
        env.setdefault("TORCH_DEVICE", "mps")

    timeout_seconds = float(env.get("DEPTHFLOW_TIMEOUT_SECONDS", "900"))
    completed = subprocess.run(
        command,
        cwd=ROOT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    if completed.returncode != 0:
        message = _tail("\n".join((completed.stdout, completed.stderr)))
        raise DepthFlowRenderError(message or "DepthFlow render failed")
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise DepthFlowRenderError("DepthFlow did not produce an MP4")
    return output_path


def find_depthflow_binary() -> Path:
    configured = os.environ.get("DEPTHFLOW_BIN")
    candidates = [
        Path(configured).expanduser() if configured else None,
        DEFAULT_LOCAL_DEPTHFLOW,
        Path(found) if (found := shutil.which("depthflow")) else None,
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate.resolve()
    raise DepthFlowUnavailable(
        "DepthFlow renderer is not installed. Set DEPTHFLOW_BIN or create .spikes/depthflow-venv."
    )


def build_depthflow_command(
    executable: Path,
    input_path: Path,
    output_path: Path,
    settings: RenderSettings,
) -> list[str]:
    return [
        str(executable),
        "input",
        "-i",
        str(input_path),
        "da2",
        "-m",
        os.environ.get("DEPTHFLOW_DA2_MODEL", "small"),
        *_motion_args(settings),
        "h264",
        "--preset",
        os.environ.get("DEPTHFLOW_H264_PRESET", "fast"),
        "--crf",
        os.environ.get("DEPTHFLOW_H264_CRF", "18"),
        "main",
        "--ratio",
        settings.aspect_ratio,
        "-h",
        str(settings.height),
        "-f",
        str(settings.fps),
        "-t",
        str(settings.duration_seconds),
        "-o",
        str(output_path),
        "-r",
        "--no-turbo",
    ]


def _motion_args(settings: RenderSettings) -> list[str]:
    intensity = _strength_intensity(settings.strength)
    if settings.preset == "orbit":
        return ["orbital", "-i", f"{intensity:.2f}", "--zoom", "0.91"]
    if settings.preset == "zoom_in":
        return [
            "zoom",
            "-i",
            f"{intensity:.2f}",
            "--no-loop",
            "horizontal",
            "-i",
            "0.10",
            "--no-loop",
        ]
    if settings.preset == "zoom_in_out":
        return [
            "zoom",
            "-i",
            f"{intensity:.2f}",
            "horizontal",
            "-i",
            "0.08",
        ]
    if settings.preset == "drift":
        return [
            "horizontal",
            "-i",
            f"{intensity * 0.22:.2f}",
            "vertical",
            "-i",
            f"{intensity * 0.10:.2f}",
        ]
    if settings.preset == "push_pull":
        return ["dolly", "-i", f"{intensity:.2f}", "horizontal", "-i", "0.05"]
    if settings.preset == "vertical_float":
        return ["vertical", "-i", f"{intensity:.2f}", "horizontal", "-i", "0.04"]
    if settings.preset == "zoom_out":
        return [
            "zoom",
            "-i",
            f"{intensity:.2f}",
            "--reverse",
            "--no-loop",
            "horizontal",
            "-i",
            "0.10",
            "--reverse",
            "--no-loop",
        ]
    raise DepthFlowRenderError(f"Unsupported preset for DepthFlow: {settings.preset}")


def _strength_intensity(strength: str) -> float:
    named = {
        "safe": 0.40,
        "soft": 0.48,
        "medium": 0.58,
        "strong": 0.68,
    }
    return named.get(strength, named["safe"])


def _tail(text: str, limit: int = 2400) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[-limit:]
