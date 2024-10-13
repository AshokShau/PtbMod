import logging
from datetime import datetime

from .__version__ import __version__

__copyright__ = (
    f"Copyright 202 - {datetime.now().year} AshokShau <github.com/AshokShau>"
)

log = logging.getLogger(__name__)
log.info(f"Version: {__version__}\nCopyright: {__copyright__}")

from .decorator import TelegramHandler
from .decorator import verify_anonymous_admin, Admins

__all__ = [
    "TelegramHandler",
    "verify_anonymous_admin",
    "Admins",
]
