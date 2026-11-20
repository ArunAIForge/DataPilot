"""The AutoGen team: Planner -> Coder -> Executor -> Reviewer, looping until APPROVED or the message cap."""
from __future__ import annotations

import re
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.conditions import FunctionalTermination, MaxMessageTermination
from autogen_agentchat.teams import SelectorGroupChat

from . import prompts
from .config import Settings
from .llm import build_client
from .sandbox import approval, build_executor

AGENTS = ["Planner", "Coder", "Executor", "Reviewer"]
ERROR_RE = re.compile(r"Traceback|Error\b|exit code:? [1-9]|No code blocks|not approved|blocked", re.I)


def is_error(text: str) -> bool:
    return bool(ERROR_RE.search(text or ""))


APPROVED_RE = re.compile(r"(?<![A-Za-z])(?<!not )APPROVED(?![A-Za-z])", re.I)  # whole word, any case, not "not approved"


def reviewer_approved(messages) -> bool:
    """True when a Reviewer message contains the word APPROVED (any case, but not 'not approved')."""
    return any(m.source == "Reviewer" and isinstance(getattr(m, "content", None), str)
               and bool(APPROVED_RE.search(m.content)) for m in messages)


def next_speaker(messages) -> str | None:
    """Deterministic loop (no LLM call): the path is decided by what just happened at run time."""
    last = messages[-1]
    src, text = last.source, getattr(last, "content", "") or ""
    if src == "Planner":
        return "Coder"
    if src == "Coder":
        return "Executor"
    if src == "Executor":
        return "Coder" if is_error(text) else "Reviewer"  # error -> Coder fixes its own code
    if src == "Reviewer":
        return "Coder"  # not approved -> back to Coder
    return "Planner"  # the human's question


def build_team(settings: Settings, workdir: Path, mock_script=None):
    def agent(name, system, desc):
        return AssistantAgent(name, model_client=build_client(settings, name, mock_script),
                              system_message=system, description=desc)

    planner = agent("Planner", prompts.PLANNER, "Writes the step-by-step analysis plan.")
    coder = agent("Coder", prompts.CODER, "Writes and repairs pandas/matplotlib code.")
    reviewer = agent("Reviewer", prompts.REVIEWER, "Checks the result, replies APPROVED when done.")
    executor = CodeExecutorAgent("Executor", code_executor=build_executor(workdir, settings),
                                 approval_func=approval, description="Runs the code in the sandbox.")
    stop = FunctionalTermination(reviewer_approved) | MaxMessageTermination(settings.max_messages)
    return SelectorGroupChat(
        [planner, coder, executor, reviewer],
        model_client=build_client(settings, "selector", mock_script),  # unused: selector_func decides
        termination_condition=stop,
        selector_func=next_speaker,
        allow_repeated_speaker=True,
    )
