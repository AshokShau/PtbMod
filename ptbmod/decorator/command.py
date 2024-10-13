from typing import Any, Callable, List, Optional, Pattern, Union

from telegram.ext import Application, CallbackQueryHandler, ChatMemberHandler, InlineQueryHandler
from telegram.ext import filters as filters_module
from telegram.ext.filters import BaseFilter

from .handlers import NewCommandHandler as CommandHandler
from .handlers import NewMessageHandler as MessageHandler


class TelegramHandler:
    """
    A class to handle adding handlers to a Telegram Application.

    This class is used to create decorators to add handlers to a Telegram Application.
    """

    def __init__(self, application: Application) -> None:
        """
        Initialize the TelegramHandler.

        Args:
            application: The Telegram Application to add the handlers to.
        """
        self.app = application

    def command(
        self,
        command: List[str],
        filters: Optional[filters_module.BaseFilter] = None,
        block: Optional[bool] = True,
        has_args: Optional[Union[bool, int]] = None,
        group: Optional[int] = 0,
        allow_edit: Optional[Union[bool, bool]] = False,
        prefix: Optional[List[str]] = None,
    ) -> Callable[[Any], None]:
        """
        A decorator to add a CommandHandler to the Telegram Application.

        Args:
            command: The command or list of commands this handler should listen for.
            filters: The filters to use for this handler. The filters are used to determine
                whether the handler should be called for a particular update.
            block: Whether the handler should block other handlers from being called.
            has_args: Whether the handler should be called with arguments.
            group: The group to add the handler to.
            allow_edit: Whether the handler should be called for edited messages.
            prefix: The prefix to use for the command.

        Returns:
            A decorator that adds the CommandHandler to the Telegram Application.
        """
        if allow_edit:
            filters = filters
        elif filters:
            filters = filters & ~filters_module.UpdateType.EDITED_MESSAGE
        else:
            filters = ~filters_module.UpdateType.EDITED_MESSAGE

        def _command(func) -> None:
            """
            A decorator to add a CommandHandler to the Telegram Application.

            This function adds the CommandHandler to the Telegram Application. The CommandHandler
            is created with the given command, filters, block, has_args, group, and prefix.

            Args:
                func: The function to call when the CommandHandler matches.

            Returns:
                The function with the CommandHandler added to the Telegram Application.
            """
            # Add the CommandHandler to the Telegram Application
            self.app.add_handler(
                CommandHandler(
                    command,
                    func,
                    filters=filters,
                    block=block,
                    has_args=has_args,
                    prefix=prefix,
                ),
                group,
            )
            return func

        return _command

    def message(
        self,
        filters: BaseFilter | None = None,
        block: Optional[bool] = True,
        allow_edit: Optional[Union[bool, bool]] = False,
        group: Optional[int] = 0,
    ) -> Callable[[Any], None]:
        """
        A decorator to add a MessageHandler to the Telegram Application.

        Args:
            filters: The filters to use for this handler. The filters are used to determine
                whether the handler should be called for a particular update.
            block: Whether the handler should block other handlers from being called.
            allow_edit: Whether the handler should be called for edited messages.
            group: The group to add the handler to.

        Returns:
            A decorator that adds the MessageHandler to the Telegram Application.
        """
        def _message(func) -> None:
            """
            A decorator to add a MessageHandler to the Telegram Application.

            This function adds the MessageHandler to the Telegram Application. The MessageHandler
            is created with the given filters, block, allow_edit, and group.

            Args:
                func: The function to call when the MessageHandler matches.

            Returns:
                The function with the MessageHandler added to the Telegram Application.
            """
            # Add the MessageHandler to the Telegram Application
            self.app.add_handler(
                MessageHandler(
                    filters=filters,
                    callback=func,
                    block=block,
                    allow_edit=allow_edit,
                ),
                group,
            )
            return func

        return _message

    def callback_query(
        self, pattern: str = None, block: Optional[bool] = True
    ) -> Callable[[Any], None]:
        """
        A decorator to add a CallbackQueryHandler to the Telegram Application.

        Args:
            pattern: The pattern to use to match the callback queries.
            block: Whether the handler should block other handlers from being called.

        Returns:
            A decorator that adds the CallbackQueryHandler to the Telegram Application.
        """
        def _callback_query(func) -> None:
            """
            A decorator to add a CallbackQueryHandler to the Telegram Application.

            This function adds the CallbackQueryHandler to the Telegram Application. The
            CallbackQueryHandler is created with the given pattern and block.

            Args:
                func: The function to call when the CallbackQueryHandler matches.

            Returns:
                The function with the CallbackQueryHandler added to the Telegram Application.
            """
            # Add the CallbackQueryHandler to the Telegram Application
            self.app.add_handler(
                CallbackQueryHandler(
                    callback=func, pattern=pattern, block=block
                )
            )
            return func

        return _callback_query

    def inline_query(
        self,
        pattern: Optional[Union[str, Pattern[str]]] = None,
        block: Optional[bool] = True,
        chat_types: Optional[List[str]] = None,
    ) -> Callable[[Any], None]:
        """
        A decorator to add an InlineQueryHandler to the Telegram Application.

        Args:
            pattern: The pattern to use to match the inline queries.
            block: Whether the handler should block other handlers from being called.
            chat_types: The types of chats to which the handler should be limited.

        Returns:
            A decorator that adds the InlineQueryHandler to the Telegram Application.
        """
        def _inline_query(func) -> None:
            """
            A decorator to add an InlineQueryHandler to the Telegram Application.

            This function adds the InlineQueryHandler to the Telegram Application. The
            InlineQueryHandler is created with the given pattern, block, and chat_types.

            Args:
                func: The function to call when the InlineQueryHandler matches.

            Returns:
                The function with the InlineQueryHandler added to the Telegram Application.
            """
            # Add the InlineQueryHandler to the Telegram Application
            self.app.add_handler(
                InlineQueryHandler(
                    callback=func, pattern=pattern, block=block, chat_types=chat_types
                )
            )
            return func

        return _inline_query

    def chat_member(
        self,
        chat_member_types: int = -1,
        block: Optional[bool] = True,
        group: Optional[int] = 0,
    ) -> Callable[[Any], None]:
        """
        A decorator to add a ChatMemberHandler to the Telegram Application.

        Args:
            chat_member_types: The types of chat members to listen for.
                If -1, listen for all types of chat members.
            block: Whether the handler should block other handlers from being called.
            group: The group to add the handler to.

        Returns:
            A decorator that adds the ChatMemberHandler to the Telegram Application.
        """

        def _chat_member(func) -> None:
            """
            A decorator to add a ChatMemberHandler to the Telegram Application.

            This function adds the ChatMemberHandler to the Telegram Application. The
            ChatMemberHandler is created with the given chat_member_types, block, and group.

            Args:
                func: The function to call when the ChatMemberHandler matches.

            Returns:
                The function with the ChatMemberHandler added to the Telegram Application.
            """
            # Add the ChatMemberHandler to the Telegram Application
            self.app.add_handler(ChatMemberHandler(func, chat_member_types, block), group)
            return func

        return _chat_member
