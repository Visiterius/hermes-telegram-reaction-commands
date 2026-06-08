from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SetupState:
    chat_id: str
    user_id: str
    step: int = 0
    reactions: list[str] = field(default_factory=list)
    raw_meanings: Dict[str, str] = field(default_factory=dict)
    polished_meanings: Dict[str, str] = field(default_factory=dict)
    awaiting_approval: bool = False


def numbered_reaction_prompt(reactions: list[str]) -> str:
    lines = ["Choose meanings for your Telegram reactions:", ""]
    for i, emoji in enumerate(reactions, start=1):
        lines.append(f"{i}. {emoji} - meaning?")
    lines.append("")
    lines.append("Reply like: `1 = approve/proceed`, then continue with each number.")
    return "\n".join(lines)


def next_missing_reaction(state: SetupState) -> Optional[tuple[int, str]]:
    for idx, emoji in enumerate(state.reactions, start=1):
        if emoji not in state.raw_meanings:
            return idx, emoji
    return None


def build_polish_prompt(raw_meanings: Dict[str, str]) -> str:
    mapping = "\n".join(f"{emoji}: {meaning}" for emoji, meaning in raw_meanings.items())
    return f"""Refactor these raw Telegram reaction command meanings into concise, safe Hermes instructions.

Rules:
- Preserve the user's intent.
- Make each instruction actionable.
- If a meaning implies approval/proceed/destructive action, scope it to the specific reacted message and pending action only.
- Do not grant global permission.
- Return a clear mapping only.

Raw mapping:
{mapping}
"""


def render_approval_message(polished_meanings: Dict[str, str]) -> str:
    lines = ["Proposed reaction command map:", ""]
    for emoji, meaning in polished_meanings.items():
        lines.append(f"{emoji} = {meaning}")
    lines.append("")
    lines.append("Reply `approve` to activate, or `edit <emoji> = <meaning>` to change one.")
    return "\n".join(lines)
