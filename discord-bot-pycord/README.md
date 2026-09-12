# TemplateBot

Discord bot generated with [Templetry](https://github.com/Templetry): [py-cord](https://docs.pycord.dev/), src layout, cogs per capability, pytest.

## Setup

1. Create an application + bot at the [Discord Developer Portal](https://discord.com/developers/applications). Enable the **Message Content** and **Server Members** privileged intents.
2. Invite the bot with the `bot` + `applications.commands` scopes and permissions matching the enabled cogs (Manage Messages, Kick/Ban Members, Manage Roles, Connect/Speak).
3. Install and run:

```sh
pip install -e .[dev]
cp .env.example .env   # fill in DISCORD_TOKEN
template-bot
pytest
```

## Cogs

- `moderation` — kick, ban, purge
- `welcome` — greets new members, optional auto-role
- `music` — voice channel playback via yt-dlp (requires `ffmpeg` on the host)
- `utility` — ping, uptime (always included)
