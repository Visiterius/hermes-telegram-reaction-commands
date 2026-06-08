from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from .ascii_greeting import greeting
from .config_store import ChatReactionConfig
from .constants import DEFAULT_SAFE_MEANINGS, UNAVAILABLE_REACTION_COMMAND_EMOJIS, VISIBLE_REACTIONS_FROM_SCREENSHOT
from .setup_flow import render_approval_message


@dataclass
class CommandFlowResult:
    handled: bool
    reply: str
    config: ChatReactionConfig | None = None
    delete_requested: bool = False


def parse_mapping_reply(text: str, reactions: Iterable[str] = VISIBLE_REACTIONS_FROM_SCREENSHOT) -> Dict[str, str]:
    """Parse setup replies like `2 = approve` or `🤓 = research deeper`."""
    reaction_list = list(reactions)
    mapping: Dict[str, str] = {}
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        left, right = [part.strip() for part in line.split("=", 1)]
        if not right:
            continue
        emoji = left
        if left.isdigit():
            idx = int(left)
            if 1 <= idx <= len(reaction_list):
                emoji = reaction_list[idx - 1]
            else:
                continue
        if emoji in reaction_list and emoji not in UNAVAILABLE_REACTION_COMMAND_EMOJIS:
            mapping[emoji] = right
    return mapping


def safe_default_mapping() -> Dict[str, str]:
    """Return the curated safe starter mapping."""
    return dict(DEFAULT_SAFE_MEANINGS)


def handle_setup_approval(chat_id: str, user_id: str, raw_mapping: Dict[str, str]) -> CommandFlowResult:
    """Create an enabled config from approved setup meanings."""
    allowed = set(VISIBLE_REACTIONS_FROM_SCREENSHOT) - set(UNAVAILABLE_REACTION_COMMAND_EMOJIS)
    filtered = {emoji: meaning for emoji, meaning in raw_mapping.items() if emoji in allowed and meaning.strip()}
    polished = {**safe_default_mapping(), **filtered}
    config = ChatReactionConfig(chat_id=chat_id, user_id=user_id, enabled=True, map=polished)
    reply = render_approval_message(polished) + "\n\n" + greeting()
    return CommandFlowResult(handled=True, reply=reply, config=config)


def handle_delete_command(chat_id: str, user_id: str, text: str) -> CommandFlowResult:
    """Handle `/delete` confirmation text for chat config removal."""
    normalized = (text or "").strip().lower()
    if normalized in {"/delete", "delete"}:
        return CommandFlowResult(
            handled=True,
            reply="Delete Telegram reaction-command config for this chat? Reply `delete yes`.",
        )
    if normalized == "delete yes":
        return CommandFlowResult(
            handled=True,
            reply="Telegram reaction-command config deleted for this chat.",
            delete_requested=True,
            config=ChatReactionConfig(chat_id=chat_id, user_id=user_id),
        )
    if normalized == "/delete plugin":
        return CommandFlowResult(
            handled=True,
            reply="Full uninstall: remove the plugin directory, remove `telegram.reaction_commands` from config.yaml, then restart the Hermes gateway.",
        )
    return CommandFlowResult(handled=False, reply="")
