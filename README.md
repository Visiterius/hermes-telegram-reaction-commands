# Telegram Reaction Commands for Hermes

Independent community plugin/prototype for mapping Telegram message reactions to scoped Hermes Agent commands.


## What it does

A Telegram user reacts to an assistant message, and the reaction is resolved into a structured command/action.

Safe default shortcuts use only reactions that were visible in the Telegram reaction picker during testing:

- `💯` = approve/proceed only for the exact reacted assistant message when it has an active pending action attached.
- `🤓` = research the reacted answer or claim deeper.
- `👀` = verify/check current status with tools where possible.
- `✍️` = rewrite or clean up the reacted answer into a clearer, shorter version.
- `💅` = polish wording, structure, and presentation.
- `🤔` = critique assumptions, risks, missing details, or weak logic.
- `👨‍💻` = inspect or improve code/dev implementation details.

## Important Telegram constraint

Telegram reactions are **not arbitrary emojis**. Users can only pick from the reaction set exposed by Telegram for that chat/account. Premium/custom reactions may be locked or unavailable.

Known-unavailable for this test flow: `🧹` and `🔁`. They are good concepts, but they are not usable shortcuts if Telegram does not expose them as message reactions.

## Current status

This is currently a **standalone plugin/prototype package**, not a fully installable Hermes production plugin yet.

Reason: Hermes Telegram gateway currently needs a core bridge/hook that emits raw Telegram `MessageReactionUpdated` events to plugins. Until that hook exists, this repo provides the tested command-routing, setup-flow, config-storage, and safety logic that such a plugin would use.

## Safety model

- Only authorized Telegram users should configure or trigger reactions.
- Reaction actions are scoped to the message being reacted to.
- `approve/proceed` reactions must only work against a stored pending-action ID for the exact target message.
- Dangerous/destructive actions still require stronger confirmation unless Hermes core approval already allows them.
- Reaction removal does not undo already executed actions.
- Reactions to old/untracked messages are ignored or return a short notice.

## Prototype UX target

### `/setup`

1. Detect Telegram gateway context.
2. Show numbered available/default reaction list.
3. For each reaction, ask the user to type its meaning.
4. Store raw user meanings temporarily.
5. Ask Hermes/LLM to refactor/polish the raw meanings into safe, clear command prompts.
6. Show the proposed mapping back to the user.
7. Require explicit approval before activation.
8. On approval, write plugin config and send a glitch-style greeting.

### `/delete`

1. Ask confirmation.
2. Disable/delete plugin config for the current bot/profile/chat.
3. Remove pending setup state.
4. Send confirmation with uninstall instructions if needed.

## Architecture

```text
Telegram Update: MessageReactionUpdated
  -> Telegram gateway reaction bridge/hook
  -> reaction plugin router
  -> config lookup: chat/profile/user mapping
  -> target message lookup: bot message id -> session/message metadata
  -> action resolver
  -> inject scoped user instruction OR approve exact pending action
  -> send acknowledgment
```

## Repository shape

```text
hermes-telegram-reaction-commands/
  README.md
  LICENSE
  pyproject.toml
  plugin.yaml
  reaction_commands/
    __init__.py
    constants.py
    config_store.py
    setup_flow.py
    reaction_router.py
    command_flow.py
    ascii_greeting.py
  tests/
    test_core.py
```

## Local development

```bash
python -m pytest -q
```

Expected result:

```text
10 passed
```

## Future install target

Once Hermes exposes a plugin hook for Telegram reaction events, intended install shape could be:

```bash
hermes plugins install https://github.com/Visiterius/hermes-telegram-reaction-commands
hermes gateway restart
```

For now, treat this repository as an independent prototype/reference implementation.
