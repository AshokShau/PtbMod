from collections.abc import Callable
from functools import wraps, partial
from typing import Optional, Union, Any

from telegram import Update, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatID, ChatType
from telegram.ext import ContextTypes

from .cache import get_admin_cache_user, is_admin, is_owner, load_admin_cache
from ..config import Config


def ensure_permissions_list(permissions: Union[str, list[str]]) -> list[str]:
    """
    Ensures permissions are a list of strings.
    """
    if isinstance(permissions, str):
        return [permissions]
    return permissions or []


async def check_permissions(chat_id: int, user_id: int, permissions: Union[str, list[str]]) -> bool:
    """
    Check if a user has specific permissions.
    """
    permissions = ensure_permissions_list(permissions)
    if not permissions:
        return True

    if await is_owner(chat_id, user_id):
        return True

    if not await is_admin(chat_id, user_id):
        return False

    _, user_info = await get_admin_cache_user(chat_id, user_id)
    if not user_info:
        return False

    return all(getattr(user_info, perm, False) for perm in permissions)


async def verifyAnonymousAdmin(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[Union[Message, bool]]:
    callback = update.callback_query
    callback_id = int(f"{callback.message.chat.id}{callback.data.split('.')[1]}")
    message, func, permissions = context.bot_data.pop(callback_id, (None, None, None))

    if not message:
        await callback.answer("Failed to get message", show_alert=True)
        await callback.delete_message()
        return

    if not await check_permissions(message.chat.id, callback.from_user.id, permissions):
        await callback.answer("You don't have the required permissions.", show_alert=True)
        await callback.delete_message()
        return

    try:
        await callback.delete_message()
        await func(update, context)
    except Exception as e:
        raise e


def Admins(
        permissions: Optional[Union[str, list[str]]] = None,
        is_bot: bool = False,
        is_user: bool = False,
        is_both: bool = False,
        only_owner: bool = False,
        no_reply: bool = False,
        allow_pm: bool = True,
        only_devs: bool = False
) -> Callable[[Any], Any]:
    """
    Decorator to check if a specific user or bot has required permissions.
    """
    permissions = ensure_permissions_list(permissions)

    def wrapper(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Union[
            Message, Any, None]:
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            bot_id = context.bot.id
            message = update.effective_message
            sender = partial(update.callback_query.answer, show_alert=True) if isinstance(update.callback_query,
                                                                                          CallbackQuery) else message.reply_text

            if only_devs and user_id not in Config.DEVS:
                if no_reply:
                    return None
                return await sender("Only developers can use this command.")

            if not allow_pm and update.effective_chat.type == ChatType.PRIVATE:
                if no_reply:
                    return None
                return await sender("This command can only be used in groups.")

            load, _ = await load_admin_cache(context.bot, chat_id)
            if not load:
                if no_reply:
                    return None
                return await sender("I need to be an admin to do this.")

            if message.from_user.id == ChatID.ANONYMOUS_ADMIN and not no_reply:
                context.bot_data[int(f"{message.chat.id}{message.id}")] = (message, func, permissions)
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Verify Admin", callback_data=f"anon.{message.id}")]])
                return await message.reply_text(
                    "Please verify that you are an admin to perform this action.",
                    reply_markup=keyboard,
                )

            if only_owner and not await is_owner(chat_id, user_id):
                if no_reply:
                    return None
                return await sender("Only the chat owner can use this command.")

            async def check_and_notify(subject_id, subject_name) -> Optional[bool]:
                if not await is_admin(chat_id, subject_id):
                    if no_reply:
                        return None
                    await sender(f"{subject_name} needs to be an admin.")
                    return False

                if not await check_permissions(chat_id, subject_id, permissions):
                    if no_reply:
                        return None
                    await sender(f"{subject_name} lacks required permissions: {', '.join(permissions)}.")
                    return False
                return True

            if is_bot and not await check_and_notify(bot_id, "I"):
                return None
            if is_user and not await check_and_notify(user_id, "You"):
                return None
            if is_both:
                if not await check_and_notify(user_id, "You") or not await check_and_notify(bot_id, "I"):
                    return None

            return await func(update, context, *args, **kwargs)

        return wrapped

    return wrapper
