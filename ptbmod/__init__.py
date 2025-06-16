from datetime import datetime

from .__version__ import __version__

__copyright__ = (
    f"Copyright © {datetime.now().year} AshokShau <github.com/AshokShau>"
)

print(f"PtbMod Version: {__version__}\n{__copyright__}")

from .decorator import TelegramHandler
from .decorator import verifyAnonymousAdmin, Admins

__all__ = [
    "TelegramHandler",
    "verifyAnonymousAdmin",
    "Admins",
]
