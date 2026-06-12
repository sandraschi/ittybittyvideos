"""One-shot short video render (custom script = no LLM key required)."""
from __future__ import annotations

import asyncio
import sys
import time

from videogen_mcp.models.schema import GenerateRequest, JobStatus, VideoAspect
from videogen_mcp.services.pipeline import generate_video, get_job

SCRIPT = """\
Cats are fascinating companions. They sleep up to sixteen hours a day and still find time to judge you.

Their purring may help heal bones and reduce stress in humans. Science still argues about why they purr.

Every cat has a unique nose print, like a human fingerprint. No two toe beans are alike.\
"""


async def main() -> int:
    req = GenerateRequest(
        script=SCRIPT,
        aspect=VideoAspect.PORTRAIT,
        paragraph_count=3,
        clip_duration=5.0,
    )
    job = await generate_video(req)
    print(f"job_id={job.job_id} status={job.status.value}")

    for _ in range(180):
        await asyncio.sleep(2)
        j = get_job(job.job_id)
        if not j:
            print("job lost")
            return 1
        print(f"  {j.status.value} {j.progress:.0f}%")
        if j.status == JobStatus.COMPLETE:
            print(f"OK output={j.output_path}")
            return 0
        if j.status == JobStatus.FAILED:
            print(f"FAIL {j.error}")
            return 1
    print("timeout")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
