Ptbmod
================

A Python Patch for `python-telegram-bot` with Decorator Support
---------------------------------------------------------

### Overview

Ptbmod is a patch for the popular `python-telegram-bot` library that introduces decorator support for cleaner and more efficient handling of commands and messages within your Telegram bot applications.

### Key Features

* **Command and Message Handlers**: Simplify the process of registering command and message handlers with the `TelegramHandler`.
* **Admin Decorators**: Easily check user permissions directly in your command functions with decorators like `@Admins` and `verify_anonymous_admin`.

### Installation

To install ptbmod, run the following command:
```bash
pip install ptbmod
```
Or, to install with additional dependencies:
```bash
pip install ptbmod[all]
```
### Usage

To utilize the new decorators and handlers, follow these steps:

1. Import the necessary modules:

```python
from ptbmod import TelegramHandler, verifyAnonymousAdmin, Admins
```

2. Create a `TelegramHandler` instance:
```python
Cmd = TelegramHandler(application).command
Msg = TelegramHandler(application).message
```

3. Define your bot commands and message handlers using the `Cmd` and `Msg` shortcuts:
```python
@Cmd(command=["start", "help"])
@Admins(is_both=True)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Command handler code here
```
### Example

For a complete example, see the [example code](#example) below.

### Requirements

* `python-telegram-bot`
* `cachetools`
* `python-dotenv`

### License

Ptbmod is licensed under the [MIT License](/LICENSE).

### Contributing

Contributions are welcome! Please submit a pull request with your changes.

### Example

```python
import logging

from telegram import Message, Update
from telegram.ext import ApplicationBuilder, ContextTypes, filters, CallbackQueryHandler, Defaults

from ptbmod import TelegramHandler, verifyAnonymousAdmin, Admins
from ptbmod.decorator.cache import is_admin

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger('httpx').setLevel(logging.WARNING)

application = (
    ApplicationBuilder()
    .token('TOKEN')
    .arbitrary_callback_data(True)
    .defaults(Defaults(allow_sending_without_reply=True))
    .build()
)

Cmd = TelegramHandler(application).command
Msg = TelegramHandler(application).message


@Cmd(command=["start", "help"])
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send a message when the command /start or /help is issued.
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I am a bot.\nUse /kick to kick a user from the chat."
    )


@Cmd(command=["kick"])
@Admins(permissions="can_restrict_members", is_both=True, allow_pm=False)
async def ban(update: Update, _: ContextTypes.DEFAULT_TYPE) -> Message:
    """
    Kick a user from the chat.
    """
    msg = update.effective_message
    reply = msg.reply_to_message
    chat = update.effective_chat
    if not reply:
        return await msg.reply_text("Please reply to a user to kick them.")
    
    user = reply.from_user
    if await is_admin(chat.id, user.id):
        return await msg.reply_text("You can't kick an admin.")
    
    await chat.unban_member(user.id)
    return await msg.reply_text(f"Kicked user {user.full_name}")


@Msg(filters=filters.ChatType.PRIVATE & ~filters.COMMAND)
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send a message with the same text as the user's message in a private chat when the
    message is not a command.
    """
    await context.bot.copy_message(
        chat_id=update.effective_chat.id,
        from_chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )


if __name__ == '__main__':
    application.add_handler(CallbackQueryHandler(verifyAnonymousAdmin, pattern=r"^anon."))
    application.run_polling()
```