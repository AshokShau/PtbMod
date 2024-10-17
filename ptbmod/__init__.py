from datetime import datetime

from .__version__ import __version__

__copyright__ = (
    f"Copyright 202 - {datetime.now().year} AshokShau <github.com/AshokShau>"
)

print(f"Version: {__version__}\nCopyright: {__copyright__}")

from .decorator import TelegramHandler
from .decorator import verify_anonymous_admin, Admins

__all__ = [
    "TelegramHandler",
    "verify_anonymous_admin",
    "Admins",
]
