"""Canonical MCP tool catalog — drives /api/v1/tools, /api/v1/status, and videogen_help."""

from __future__ import annotations

from typing import TypedDict


class McpToolMeta(TypedDict):
    name: str
    description: str
    kind: str


MCP_TOOL_CATALOG: list[McpToolMeta] = [
    {
        "name": "videogen_help",
        "description": "Discovery: all tools, workflow hints, director pack overview.",
        "kind": "catalog",
    },
    {
        "name": "videogen_generate",
        "description": "Short video (~15–50 s) from topic or custom script.",
        "kind": "pipeline",
    },
    {
        "name": "videogen_status",
        "description": "Poll job progress by job_id.",
        "kind": "pipeline",
    },
    {
        "name": "videogen_list_jobs",
        "description": "List recent generation jobs (limit 1–50).",
        "kind": "pipeline",
    },
    {
        "name": "videogen_plan",
        "description": "Mid-length storyboard only (no render).",
        "kind": "pipeline",
    },
    {
        "name": "videogen_plan_render",
        "description": "Plan and render mid-length video (3–15 min).",
        "kind": "pipeline",
    },
    {
        "name": "videogen_review",
        "description": "Screening Room: VLM critique of a finished job (VIDEOGEN_VLM_*).",
        "kind": "pipeline",
    },
    {
        "name": "videogen_providers",
        "description": "List LLM, stock, TTS, and talker providers.",
        "kind": "catalog",
    },
    {
        "name": "videogen_structures",
        "description": "List R10 trope / structure YAML presets.",
        "kind": "catalog",
    },
    {
        "name": "videogen_intros",
        "description": "List intro sequence packs (contrast, gravitas, trailer, …).",
        "kind": "catalog",
    },
    {
        "name": "videogen_credits",
        "description": "List end-credits contributor packs.",
        "kind": "catalog",
    },
    {
        "name": "videogen_visual_look",
        "description": "AI footage look catalog (style, material, tone presets).",
        "kind": "catalog",
    },
    {
        "name": "videogen_intro_sample",
        "description": "Sample intro prompt block for a pack (accepts intro:id or bare id).",
        "kind": "catalog",
    },
    {
        "name": "videogen_credits_sample",
        "description": "Sample absurd credits roll text for a pack.",
        "kind": "catalog",
    },
    {
        "name": "videogen_depot",
        "description": "List persisted finished videos in the depot.",
        "kind": "depot",
    },
    {
        "name": "videogen_publish_pack",
        "description": "Build publish helpers (hashtags, platform links) for a completed job.",
        "kind": "depot",
    },
]

MCP_WORKFLOW_HINTS: list[str] = [
    "Short: videogen_generate(topic=..., paragraph_count=3) → videogen_status(job_id)",
    "Mid: videogen_plan → videogen_plan_render → videogen_status",
    "Director: videogen_structures + videogen_intros; pass structure= trope:… and intro= intro:… on generate/plan",
    "AI footage look: videogen_visual_look then visual_style / visual_material / visual_tone on generate",
    "After render: videogen_depot, videogen_publish_pack, optional videogen_review",
]


def mcp_tool_count() -> int:
    return len(MCP_TOOL_CATALOG)


def mcp_tools_payload() -> dict:
    return {"success": True, "tools": MCP_TOOL_CATALOG, "count": len(MCP_TOOL_CATALOG)}


def mcp_help_payload(*, mcp_enabled: bool, version: str) -> dict:
    return {
        "success": True,
        "product": "ittybitty",
        "version": version,
        "mcp_enabled": mcp_enabled,
        "mcp_endpoint": "/mcp" if mcp_enabled else None,
        "tools": MCP_TOOL_CATALOG,
        "tool_count": len(MCP_TOOL_CATALOG),
        "workflow_hints": MCP_WORKFLOW_HINTS,
    }
