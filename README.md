# Telegram reaction commands for Hermes

A small experiment for using Telegram reactions as lightweight commands for Hermes Agent.

The idea is simple: instead of replying "check this", "rewrite it", or "approve", you react to the assistant message with an emoji. Hermes can then turn that reaction into a scoped instruction for that exact message.

This is not an official Hermes Agent project. It is not a pull request against Hermes core. It is a standalone prototype for a funny but useful interaction pattern.

## Example mapping

These are the shortcuts I tested because they were available in Telegram's reaction picker:

- `👀` means check or verify the reacted message.
- `✍️` means rewrite or clean it up.
- `💅` means polish the wording/presentation.
- `🤔` means critique the logic or assumptions.
- `🤓` means research the claim more deeply.
- `👨‍💻` means inspect or improve code-related details.
- `💯` means approve, but only when the reacted message has an exact pending action attached.

The mapping does not have to stay like this. The useful part is the pattern: quick reactions become message-scoped commands.

## Current state

This repo contains the routing and safety logic for a future Hermes plugin, plus tests around the behavior.

It is not a drop-in production plugin yet. Hermes still needs a bridge/hook that passes Telegram `MessageReactionUpdated` events from the gateway into plugin code. Until that exists, this repository is best treated as a prototype/reference implementation.

## Telegram limitation

Telegram reactions are not arbitrary emojis. A user can only pick from the reactions Telegram exposes for that chat/account. Premium or custom reactions may not be available.

During testing, `🧹` and `🔁` were not usable as normal reactions, so they are not in the default map.

## Safety notes

Reaction commands should stay narrow. A reaction is a convenient shortcut, not a general permission system.

Current safety assumptions:

- Only authorized Telegram users should be allowed to configure or trigger reaction commands.
- A reaction applies to the assistant message it was attached to.
- Approval reactions require a matching pending action ID for that exact message.
- Old or unknown messages should be ignored or get a short "nothing to do" response.
- Removing a reaction does not undo work that already ran.
- Destructive actions still need stronger confirmation unless Hermes core approval logic already covers them.

## Prototype setup flow

The intended `/setup` flow is:

1. Detect the Telegram/Hermes context.
2. Show the default reaction list.
3. Ask the user what each reaction should mean.
4. Store the raw meanings temporarily.
5. Ask Hermes/LLM to turn those meanings into clear, safe command prompts.
6. Show the final mapping back to the user.
7. Require explicit approval before enabling it.
8. Save the plugin config and send a small greeting.

The intended `/delete` flow is:

1. Ask for confirmation.
2. Disable or delete the mapping for the current bot/profile/chat.
3. Clear pending setup state.
4. Confirm that the shortcut mapping was removed.

## Architecture sketch

```text
Telegram MessageReactionUpdated event
  -> Hermes Telegram gateway bridge
  -> reaction command router
  -> config lookup for chat/profile/user
  -> target message lookup
  -> action resolver
  -> scoped user instruction or exact pending-action approval
  -> short acknowledgment
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
    ascii_greeting.py
    command_flow.py
    config_store.py
    constants.py
    reaction_router.py
    setup_flow.py
  tests/
    test_core.py
```

## Local development

Run tests with:

```bash
python -m pytest -q
```

Current expected result:

```text
12 passed
```

## Possible install shape later

If Hermes exposes the needed Telegram reaction plugin hook, installation could eventually look like this:

```bash
hermes plugins install https://github.com/Visiterius/hermes-telegram-reaction-commands
hermes gateway restart
```

For now, this repo is just the standalone prototype for the idea.
