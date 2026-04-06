import asyncio
from datetime import datetime

from agentbrowser.config.settings import Settings
from agentbrowser.core.agent import build_agent


async def run_task(
    task: str,
    settings: Settings,
    llm_provider: str | None = None,
    vision: bool = False,
) -> dict:
    agent = build_agent(task, settings, llm_provider, vision)
    started_at = datetime.now()

    history = await agent.run(max_steps=settings.max_steps)

    ended_at = datetime.now()
    final = history.final_result()

    return {
        "task": task,
        "result": final if final is not None else str(history),
        "llm": llm_provider or settings.default_llm,
        "vision": vision,
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "duration_seconds": round((ended_at - started_at).total_seconds(), 2),
        "steps_taken": len(history.history),
        "success": not history.has_errors(),
    }


def run_task_sync(
    task: str,
    settings: Settings,
    llm_provider: str | None = None,
    vision: bool = False,
) -> dict:
    return asyncio.run(run_task(task, settings, llm_provider, vision))
