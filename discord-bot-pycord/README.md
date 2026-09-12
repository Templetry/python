# TemplateBot

Discord bot generated with [Templetry](https://github.com/Templetry): [py-cord](https://docs.pycord.dev/), src layout, auto-loading cogs, pytest.

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

## Architecture

Everything under `src/template_bot/cogs/` is discovered and loaded automatically at startup (`main.py`) — dropping a new cog file in is enough, nothing else needs editing.

- `config.py` — the two things that must come from the environment (token, prefix)
- `storage.py` — a small per-guild JSON store on disk (`data/guild_settings.json`, gitignored); the mechanism every other cog uses to remember configuration
- `logging_setup.py` — console logging, with the noisy `discord.http` logger turned down
- `errors.py` — a global slash-command error handler so every cog gets consistent, user-facing error messages for free

## Cogs

- `settings` — `/settings welcome_channel|auto_role|mod_log|show`, writes to `storage.py`
- `admin` — owner-only `/sync`, `/reload`, `/shutdown`
- `moderation` — `/kick`, `/ban`, `/purge`, optionally logged to the configured mod-log channel
- `welcome` — greets new members and applies an auto-role, configured via `/settings`
- `custom_commands` — `/addcommand`, `/removecommand`, `/say`: lets server admins define text responses at runtime
- `music` — voice channel playback via yt-dlp (requires `ffmpeg` on the host)
- `utility` — `/ping`, `/uptime` (always included)
