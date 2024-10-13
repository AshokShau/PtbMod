from time import perf_counter
from typing import Optional

from cachetools import TTLCache
from cachetools.keys import hashkey

from telegram import Chat, ChatMember, error
from telegram.constants import ChatMemberStatus

# Admins stay cached for 20 minutes
member_cache = TTLCache(maxsize=512, ttl=(60 * 20), timer=perf_counter)

async def get_member_with_cache(
        chat: Chat,
        user_id: int,
        force_reload: bool = False,
) -> Optional[ChatMember]:
    """
    Get a chat member with caching to avoid hitting the API rate limit.

    Args:
        chat (Chat): The Chat object to get the member from.
        user_id (int): The user id of the member to get.
        force_reload (bool): Whether to force reloading the member from the API.
            Defaults to False.

    Returns:
        Optional[Member]: The member if it is cached or if it is successfully retrieved
            from the API, None otherwise.
    """
    cache_key = hashkey(chat.id, user_id)
    if not force_reload and cache_key in member_cache:
        return member_cache[cache_key]

    try:
        member = await chat.get_member(user_id)
    except (error.BadRequest, error.Forbidden):
        return None
    except Exception as e:
        raise e

    member_cache[cache_key] = member
    return member

def is_admin(member: ChatMember) -> bool:
    """
    Checks if a ChatMember is an admin or the owner of the chat.

    Args:
        member (ChatMember): The member to check.

    Returns:
        bool: True if the member is an admin or the owner.
    """
    return member and member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
