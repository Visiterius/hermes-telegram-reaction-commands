VISIBLE_REACTIONS_FROM_SCREENSHOT = [
    "🙏", "💯", "💅", "✍️", "🤯", "🤣", "🏆", "🫡",
    "😍", "😁", "🎃", "🙊", "❤️", "😔", "😭", "🤩",
    "🤓", "👎", "🤔", "🔥", "🥰", "🤪", "👍", "👏",
    "😱", "🤬", "🎉", "🤮", "💩", "👌", "🕊️", "🤡",
    "🥱", "😟", "🐳", "❤️‍🔥", "🌚", "🌭", "⚡", "🍌",
    "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈",
    "😴", "👻", "👨‍💻", "👀", "😇", "😨", "🤝", "🤗",
]

DEFAULT_SAFE_MEANINGS = {
    "💯": "Approve/proceed only if the reacted assistant message has an active pending action attached to that exact message. Do not grant global permission.",
    "🤓": "Research the topic or claim in the reacted assistant message and return a practical, source-grounded summary.",
    "👀": "Verify/check current status of the reacted assistant message using tools where possible.",
    "✍️": "Rewrite or clean up the reacted assistant message into a clearer, shorter version without changing meaning.",
    "💅": "Polish the reacted assistant message: improve wording, structure, and presentation.",
    "🤔": "Critique the reacted assistant message: check assumptions, risks, missing details, or weak logic.",
    "👨‍💻": "Treat the reacted assistant message as code/dev related and inspect or improve the implementation.",
}

UNAVAILABLE_REACTION_COMMAND_EMOJIS = {"🔁", "🧹"}
