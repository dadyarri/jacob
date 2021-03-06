import os

from services.logger.handlers import TelegramHandler
from services.logger.utils import on_production

fmt = "{time:YYYY-MM-DD@HH:mm:ss zz} | {module}.{function} | {level} | {message}"
extra_fmt = (
    "{time:YYYY-MM-DD@HH:mm:ss zz} | {module}.{function} | {level} | @id{"
    "extra[user_id]}: {message}"
)
tg_conf = {"token": os.getenv("TG_TOKEN"), "chat": os.getenv("TG_CHAT")}

config = {
    "handlers": [
        {
            "sink": TelegramHandler(defaults=tg_conf),
            "format": extra_fmt,
            "level": "ERROR",
            "filter": lambda record: "user_id" in record["extra"] and on_production(),
        },
        {
            "sink": TelegramHandler(defaults=tg_conf),
            "format": fmt,
            "level": "ERROR",
            "filter": lambda record: "user_id" not in record["extra"]
            and on_production(),
        },
        {
            "sink": "jacob.log",
            "format": extra_fmt,
            "rotation": "20 MB",
            "enqueue": True,
            "filter": lambda record: "user_id" in record["extra"],
        },
        {
            "sink": "jacob.log",
            "format": fmt,
            "rotation": "20 MB",
            "enqueue": True,
            "filter": lambda record: "user_id" not in record["extra"],
        },
    ],
}
