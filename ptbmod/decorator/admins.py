from functools import partial, wraps
from typing import Any, Union, Callable, Optional, List

from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update
)

from telegram.constants import ChatID, ChatType, ChatMemberStatus
from telegram.ext import ContextTypes

from ptbmod.config import Config
from .cache import get_member_with_cache, is_admin, is_owner


async def verify_anonymous_admin(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[Union[Message, bool]]:
    """
    Verify anonymous admin permissions.

    This function is called when the user presses the "Verify Admin" button.
    It checks if the button is valid, and if the user is an admin.
    If the user is an admin, it calls the function that was passed to the Admins decorator.
    """
    callback = update.callback_query
    callback_id = int(f"{callback.message.chat.id}{callback.data.split('.')[1]}")
    message, func, permissions = context.bot_data.pop(callback_id)
    if not message:
        await callback.answer("Failed to get message", show_alert=True)
        await callback.delete_message()
        return

    member = await get_member_with_cache(callback.message.chat, callback.from_user.id)
    bot = await get_member_with_cache(callback.message.chat, context.bot.id)

    # If the bot or user is None, return
    if bot is None or member is None:
        await callback.answer("Failed to get member", show_alert=True)
        return

    # Check if the user and bot are admins
    if not is_admin(bot):
        await callback.answer("I need to be an admin to do this", show_alert=True)
        return
    if not is_admin(member):
        await callback.answer("You need to be an admin to do this", show_alert=True)
        return

    # Check user permissions
    missing_permissions = []
    def check_permissions(member_privileges, permissions_list):
        """
        Check if the user has the required permissions.
        """
        if permissions_list is None:
            return
        for permission in (permissions_list if isinstance(permissions_list, list) else [permissions_list]):
            if not getattr(member_privileges, permission, False):
                missing_permissions.append(permission)

    # Check user permissions
    check_permissions(member, permissions)

    # If there are missing permissions, alert the user
    if missing_permissions and member.status != ChatMemberStatus.OWNER:
        missing_list = ", ".join(missing_permissions)
        await callback.answer(
            f"You do not have the required permissions: {missing_list}.", show_alert=True
        )
        return
    try:
        # Delete the message and call the function
        await callback.delete_message()
        await func(update, context)
    except Exception as e:
        raise e


# Permission error messages mapping
PERMISSION_ERROR_MESSAGES = {
    "can_delete_messages": "delete messages",
    "can_change_info": "change chat info",
    "can_promote_members": "promote members",
    "can_pin_messages": "pin messages",
    "can_invite_users": "invite users",
    "can_restrict_members": "restrict members",
    "can_manage_chat": "manage chat",
    "can_post_messages": "post messages",
    "can_edit_messages": "edit messages",
    "can_manage_video_chats": "manage video chats",
    "can_send_messages": "send messages",
    "can_send_media_messages": "send media messages",
    "can_send_other_messages": "send other types of messages",
    "can_send_polls": "send polls",
    "can_add_web_page_previews": "add web page previews",
    "can_manage_topics": "manage topics",
}

def Admins(
        permissions: Optional[Union[str, List[str]]] = None,
        is_bot: bool = False,
        is_user: bool = False,
        is_both: bool = False,
        only_owner: bool = False,
        only_dev: bool = False,
        no_reply: bool = False,
        allow_pm: bool = True,
) -> Callable[[Any], Any]:
    """
    A decorator to check if the user is an admin in the chat.

    Args:
        permissions: List of permissions that the user must have to execute the command.
        is_bot: If True, checks if the bot is an admin.
        is_user: If True, checks if the user is an admin.
        is_both: If True, checks if both the bot and user are admins.
        only_owner: If True, only the chat owner can run the command.
        only_dev: If True, only the developers can run the command.
        no_reply: If True, disables replies to the user.
        allow_pm: If True, allows command execution in private messages.

    Returns:
        A decorator that checks if the user is an admin in the chat.
    """

    def wrapper(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Optional[
            Union[Message, bool]]:
            """
            Checks if the user is an admin in the chat, and if so, executes the command.
            """
            chat = update.effective_chat
            user = update.effective_user
            bot = context.bot
            message: Union[CallbackQuery, Message] = update.effective_message
            sender = partial(update.callback_query.answer, show_alert=True) if isinstance(update.callback_query, CallbackQuery) else update.effective_message.reply_text

            # If the command is sent in a private message and allow_pm is False, return
            if message.chat.type == ChatType.PRIVATE and not only_dev:
                if allow_pm:
                    return await func(update, context, *args, **kwargs)
                elif no_reply:
                    return None
                else:
                    return await sender("This command can't be used in PM.")

            # If only_dev is True and the user is not the developer, return
            if only_dev and user.id not in Config.DEVS:
                if no_reply:
                    return None
                else:
                    return await sender("This command can only be used by the developers.")

            # If the user is an anonymous admin, ask for verification
            if message.from_user.id == ChatID.ANONYMOUS_ADMIN and not no_reply:
                context.bot_data[int(f"{message.chat.id}{message.id}")] = (message, func, permissions)
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Verify Admin", callback_data=f"anon.{message.id}")]])
                return await message.reply_text(
                         "Please verify that you are an admin to perform this action.",
                          reply_markup=keyboard,
                )

            # Get the bot and user's member information
            bot = await get_member_with_cache(chat, bot.id)
            user = await get_member_with_cache(chat, user.id)

            # If the bot or user is None, return
            if bot is None or user is None:
                return await sender("Could not retrieve member information.")

            # If only_owner is True and the user is not the chat owner, return
            if only_owner and not is_owner(user):
                if no_reply:
                    return None
                return await sender("Only the chat owner can run this command.")

            # If the bot or user is not an admin, return
            if is_bot and not is_admin(bot):
                return await sender("I need to be an admin to do this.")
            if is_user and not is_admin(user):
                return await sender("You need to be an admin to do this.")
            if is_both and not is_admin(bot) and not is_admin(user):
                return await sender("I need to be an admin and you need to be an admin to do this.")

            # Check permissions
            missing_permissions = []

            def check_permissions(member_privileges, permissions_list):
                if permissions_list is None:
                    return
                for permission in (permissions_list if isinstance(permissions_list, list) else [permissions_list]):
                    if not getattr(member_privileges, permission, False):
                        missing_permissions.append(permission)

            if is_bot:
                check_permissions(bot, permissions)
                # If the bot is missing any permissions, return
                if missing_permissions:
                    return await sender(f"I don't have permission to {', '.join(PERMISSION_ERROR_MESSAGES.get(p, p) for p in missing_permissions)}.")

            if is_user:
                check_permissions(user, permissions)
                # If the user is missing any permissions, return
                if missing_permissions and not is_owner(user):
                    return await sender(f"You don't have permission to {', '.join(PERMISSION_ERROR_MESSAGES.get(p, p) for p in missing_permissions)}.")

            if is_both:
                if not is_admin(bot):
                    return await sender("I need to be an admin to do this.")
                if not is_admin(user):
                    return await sender("You need to be an admin to do this.")

                check_permissions(bot, permissions)
                # If the bot is missing any permissions, return
                if missing_permissions:
                    return await sender(f"I don't have permission to {', '.join(PERMISSION_ERROR_MESSAGES.get(p, p) for p in missing_permissions)}.")

                missing_permissions.clear()  # Clear for user check
                check_permissions(user, permissions)
                # If the user is missing any permissions, return
                if missing_permissions and not is_owner(user):
                    return await sender(f"You don't have permission to {', '.join(PERMISSION_ERROR_MESSAGES.get(p, p) for p in missing_permissions)}.")

            return await func(update, context, *args, **kwargs)

        return wrapped

    return wrapper
