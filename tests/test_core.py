from reaction_commands.constants import VISIBLE_REACTIONS_FROM_SCREENSHOT
from reaction_commands.command_flow import handle_delete_command, handle_setup_approval, parse_mapping_reply, safe_default_mapping
from reaction_commands.config_store import ChatReactionConfig, JsonConfigStore
from reaction_commands.reaction_router import ReactionEvent, resolve_reaction
from reaction_commands.setup_flow import SetupState, next_missing_reaction, numbered_reaction_prompt


def test_visible_reaction_list_has_hundred_and_nerd():
    assert "💯" in VISIBLE_REACTIONS_FROM_SCREENSHOT
    assert "🤓" in VISIBLE_REACTIONS_FROM_SCREENSHOT
    assert "🧹" not in VISIBLE_REACTIONS_FROM_SCREENSHOT
    assert "🔁" not in VISIBLE_REACTIONS_FROM_SCREENSHOT


def test_safe_defaults_use_only_visible_telegram_reactions():
    defaults = safe_default_mapping()
    assert "🧹" not in defaults
    assert "🔁" not in defaults
    assert {"💯", "🤓", "👀", "✍️", "💅", "🤔", "👨‍💻"}.issubset(defaults)
    assert set(defaults).issubset(set(VISIBLE_REACTIONS_FROM_SCREENSHOT))


def test_numbered_prompt():
    text = numbered_reaction_prompt(["💯", "🤓"])
    assert "1. 💯" in text
    assert "2. 🤓" in text


def test_next_missing_reaction():
    state = SetupState(chat_id="1", user_id="2", reactions=["💯", "🤓"])
    assert next_missing_reaction(state) == (1, "💯")
    state.raw_meanings["💯"] = "approve"
    assert next_missing_reaction(state) == (2, "🤓")


def test_resolve_configured_reaction():
    event = ReactionEvent(chat_id="1", user_id="2", target_message_id="3", emoji="🤓")
    decision = resolve_reaction(event, {"🤓": "Research deeper."})
    assert decision.handled is True
    assert "Research deeper" in decision.instruction


def test_approval_reaction_without_pending_action_is_not_executed():
    event = ReactionEvent(chat_id="1", user_id="2", target_message_id="3", emoji="💯")
    decision = resolve_reaction(event, {"💯": "Approve/proceed"})
    assert decision.handled is True
    assert decision.instruction is None
    assert "no pending approval" in decision.ack


def test_approval_reaction_with_pending_action_is_scoped():
    event = ReactionEvent(
        chat_id="1",
        user_id="2",
        target_message_id="3",
        emoji="💯",
        pending_action_id="pending-123",
    )
    decision = resolve_reaction(event, {"💯": "Approve/proceed"})
    assert decision.handled is True
    assert "pending-123" in decision.instruction
    assert "never treat this as global permission" in decision.instruction


def test_removed_reaction_ignored():
    event = ReactionEvent(chat_id="1", user_id="2", target_message_id="3", emoji="🤓", removed=True)
    decision = resolve_reaction(event, {"🤓": "Research deeper."})
    assert decision.handled is False


def test_parse_mapping_reply_supports_numbers_and_emoji():
    parsed = parse_mapping_reply("2 = approve\n🤓 = research\n🧹 = clean", ["🙏", "💯", "🤓"])
    assert parsed == {"💯": "approve", "🤓": "research"}


def test_handle_setup_approval_builds_enabled_config():
    result = handle_setup_approval("chat", "user", {"🤓": "research hard", "🧹": "clean"})
    assert result.handled is True
    assert result.config.enabled is True
    assert result.config.map["🤓"] == "research hard"
    assert "🧹" not in result.config.map
    assert "r3act10n" in result.reply


def test_handle_delete_command_requires_confirmation():
    first = handle_delete_command("chat", "user", "/delete")
    assert first.handled is True
    assert first.delete_requested is False
    second = handle_delete_command("chat", "user", "delete yes")
    assert second.delete_requested is True


def test_json_config_store_roundtrip_and_delete(tmp_path):
    store = JsonConfigStore(tmp_path / "reaction-commands.json")
    cfg = ChatReactionConfig(chat_id="chat", user_id="user", enabled=True, map={"💯": "approve"})
    store.save(cfg)
    loaded = store.load("chat", "user")
    assert loaded == cfg
    assert store.delete("chat", "user") is True
    assert store.load("chat", "user") is None
