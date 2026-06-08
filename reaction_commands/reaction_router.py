from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ReactionEvent:
    chat_id: str
    user_id: str
    target_message_id: str
    emoji: str
    removed: bool = False
    pending_action_id: Optional[str] = None


@dataclass
class ReactionDecision:
    handled: bool
    instruction: Optional[str] = None
    ack: Optional[str] = None
    reason: Optional[str] = None


def _looks_like_approval(meaning: str) -> bool:
    """Return whether a reaction meaning is trying to approve/proceed."""
    lowered = meaning.lower()
    approval_terms = ("approve", "approval", "proceed", "continue", "go ahead", "run it", "yes")
    return any(term in lowered for term in approval_terms)


def resolve_reaction(event: ReactionEvent, configured_meanings: Dict[str, str]) -> ReactionDecision:
    """Resolve a Telegram reaction into a safe Hermes instruction.

    This is intentionally pure/testable. The gateway layer is responsible for:
    - auth
    - target message lookup
    - pending-action lookup
    - actual injection into Hermes
    """
    if event.removed:
        return ReactionDecision(handled=False, reason="reaction removed; no undo is performed")

    meaning = configured_meanings.get(event.emoji)
    if not meaning:
        return ReactionDecision(handled=False, reason="emoji not configured")

    if _looks_like_approval(meaning) and not event.pending_action_id:
        return ReactionDecision(
            handled=True,
            ack=f"{event.emoji} seen, but no pending approval is attached to message {event.target_message_id}.",
            reason="approval reaction without exact pending action",
        )

    pending_line = (
        f"Pending action id: {event.pending_action_id}\n"
        if event.pending_action_id
        else "No pending action id is attached.\n"
    )
    instruction = (
        f"User reacted {event.emoji} to assistant message {event.target_message_id}.\n"
        f"Interpretation: {meaning}\n"
        f"{pending_line}"
        "Act only on the reacted message context. If approval is requested, use only the exact "
        "pending action id above; never treat this as global permission."
    )
    return ReactionDecision(handled=True, instruction=instruction, ack=f"{event.emoji} noted")
