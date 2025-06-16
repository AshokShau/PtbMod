from typing import Optional, Tuple, List

from cachetools import TTLCache
from telegram import ChatMember, ChatMemberOwner, ChatMemberAdministrator, Bot

admin_cache = TTLCache(maxsize=1000, ttl=15 * 60)


class AdminCache:
    def __init__(self, chat_id: int, user_info: List[ChatMember], cached: bool = True):
        self.chat_id = chat_id
        self.user_info = user_info
        self.cached = cached

    def get_user_info(self, user_id: int) -> Optional[ChatMember]:
        return next((user for user in self.user_info if user.user.id == user_id), None)


async def load_admin_cache(bot: Bot, chat_id: int, force_reload: bool = False) -> tuple[bool, AdminCache]:
    """
    Load the admin list from Telegram and cache it, unless already cached.
    Set force_reload to True to bypass the cache and reload the admin list.
    """
    # Check if the cache is already populated for the chat_id
    if not force_reload and chat_id in admin_cache:
        return True, admin_cache[chat_id]  # Return the cached data if available and reload not forced

    try:
        # Retrieve and cache the admin list
        admin_list = list(await bot.get_chat_administrators(chat_id))
        admin_cache[chat_id] = AdminCache(chat_id, admin_list)
        return True, admin_cache[chat_id]
    except Exception as e:
        print(f"Error loading admin cache for chat_id {chat_id}: {e}")
        # Return an empty AdminCache with `cached=False` if there was an error
        return False, AdminCache(chat_id, [], cached=False)


async def get_admin_cache_user(chat_id: int, user_id: int) -> Tuple[bool, Optional[ChatMember]]:
    """
    Check if the user is an admin using cached data.
    """
    admin_list = admin_cache.get(chat_id)
    if admin_list is None:
        return False, None  # Cache miss; admin list not available

    for user_info in admin_list.user_info:
        if user_info.user.id == user_id:
            return True, user_info  # User is an admin in the cached list

    return False, None  # User is not found in the cached admin list


async def is_owner(chat_id: int, user_id: int) -> bool:
    """
    Check if the user is the owner of the chat.
    """
    is_cached, user_info = await get_admin_cache_user(chat_id, user_id)
    if is_cached and isinstance(user_info, ChatMemberOwner):
        return True  # User is the owner of the chat in cached data
    return False


async def is_admin(chat_id: int, user_id: int) -> bool:
    """
    Check if the user is an admin (including the owner) in the chat.
    """
    is_cached, user_info = await get_admin_cache_user(chat_id, user_id)
    if is_cached and (isinstance(user_info, ChatMemberAdministrator) or isinstance(user_info, ChatMemberOwner)):
        return True  # User is an admin or owner in the cached data
    return False
