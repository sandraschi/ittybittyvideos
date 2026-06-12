"""2026-tier local text-to-video sidecar (Wan 2.2 default)."""

BACKENDS: dict[str, dict[str, str]] = {
    "wan22-14b": {
        "model_id": "Wan-AI/Wan2.2-T2V-A14B-Diffusers",
        "label": "Wan 2.2 T2V 14B",
        "tier": "2026",
        "fps": "16",
        "default_frames": "81",
        "default_steps": "40",
    },
    "wan22-5b": {
        "model_id": "Wan-AI/Wan2.2-TI2V-5B-Diffusers",
        "label": "Wan 2.2 TI2V 5B",
        "tier": "2026-fast",
        "fps": "24",
        "default_frames": "121",
        "default_steps": "50",
    },
    "cogvideo-2b": {
        "model_id": "THUDM/CogVideoX-2b",
        "label": "CogVideoX 2B (legacy)",
        "tier": "legacy",
        "fps": "8",
        "default_frames": "49",
        "default_steps": "40",
    },
}

DEFAULT_BACKEND = "wan22-14b"

WAN_NEGATIVE_PROMPT = (
    "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，"
    "最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，"
    "画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，"
    "杂乱的背景，三条腿，背景人很多，倒着走"
)
