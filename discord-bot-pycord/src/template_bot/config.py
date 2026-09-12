import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    token: str
    prefix: str

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.environ.get("DISCORD_TOKEN", "")
        if not token:
            raise RuntimeError("DISCORD_TOKEN is not set (check your .env file)")

        return cls(
            token=token,
            prefix=os.environ.get("BOT_PREFIX", "!"),  # tpl:var bot_prefix !
        )
