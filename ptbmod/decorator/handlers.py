from typing import Any, Dict, List, Optional, Tuple, Union

import telegram.ext as tg
from telegram import Update
from telegram.ext import filters as filters_module

from ptbmod.config import Config

FilterDataDict = Dict[str, List[Any]]


class NewCommandHandler(tg.CommandHandler):
    def __init__(
        self,
        command: Union[str, list],
        callback,
        prefix: Optional[List] = Config.HANDLER,
        **kwargs,
    ) -> None:
        """
        Initialize a NewCommandHandler.

        Args:
            command: The command or list of commands this handler should listen for.
            callback: The function to call when this handler matches.
            prefix: The prefix to use for the command.
            **kwargs: Arbitrary keyword arguments.
        """
        if prefix is None:
            prefix = ["/", "!"]
        super().__init__(command, callback, **kwargs)
        self.prefix = prefix

        if isinstance(command, str):
            self.commands = frozenset({command.lower()})
        else:
            self.commands = frozenset(x.lower() for x in command)

    def check_update(
        self, update: object
    ) -> Optional[Union[bool, Tuple[List[str], Optional[Union[bool, FilterDataDict]]]]]:
        """
        Determines whether an update should be handled by this handler.

        Args:
            update: The incoming update.

        Returns:
            A tuple containing the args and the filter result, or None if this handler
            should not handle the update.
        """
        # Check if the update is an Update and has an effective message
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            # Check if the message has text and is longer than one character
            if message.text and len(message.text) > 1:
                # Split the message text into the first word and the rest
                fst_word = message.text.split(sep=None, maxsplit=1)[0]

                # Check if the first word starts with one of the prefixes
                if len(fst_word) > 1 and any(fst_word.startswith(start) for start in self.prefix):
                    # Split the first word into the command and the bot name
                    command_parts = fst_word[1:].split("@")
                    # Add the bot name to the end of the command parts
                    command_parts.append(message.get_bot().username)

                    # Check if the command is one of the commands this handler should listen for
                    # and if the bot name matches this bot's username
                    if (
                        command_parts[0].lower() not in self.commands
                        or command_parts[1].lower() != message.get_bot().username.lower()
                    ):
                        # If not, return None
                        return None

                    # Split the rest of the message into the args
                    args = message.text.split()[1:]

                    # Check if the args are correct
                    if not self._check_correct_args(args):
                        # If not, return None
                        return None

                    # Check if the filters match
                    if filter_result := self.filters.check_update(update):
                        # If they do, return the args and the filter result
                        return args, filter_result
                    # If they don't, return False
                    return False
        # If none of the above conditions are met, return None
        return None


class NewMessageHandler(tg.MessageHandler):
    def __init__(
        self,
        filters,
        callback,
        block: Optional[bool] = True,
        allow_edit: bool = False,
    ) -> None:
        """
        Initialize a NewMessageHandler.

        filters: The filters to use for this handler. The filters are used to determine
            whether the handler should be called for a particular update.
        callback: The function to call when the handler matches.
        block: Whether the handler should block other handlers from being called.
        allow_edit: Whether the handler should be called for edited messages.
        """
        super().__init__(filters, callback, block=block)
        if allow_edit is False:
            # If allow_edit is False, remove the filters for edited messages
            self.filters &= ~(
                filters_module.UpdateType.EDITED_MESSAGE
                | filters_module.UpdateType.EDITED_CHANNEL_POST
            )
