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
from ptbmod import TelegramHandler, verify_anonymous_admin, Admins
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

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, filters, CallbackQueryHandler

from ptbmod.decorator import TelegramHandler
from ptbmod.decorator.admins import verify_anonymous_admin, Admins

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

application = ApplicationBuilder().token('TOKEN').build()

Cmd = TelegramHandler(application).command
Msg = TelegramHandler(application).message

# Define a command handler
@Cmd(command=["start", "help"])
@Admins(is_both=True)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Command handler code here
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!"
    )

# Define a message handler
@Msg(filters=filters.ChatType.PRIVATE & ~filters.COMMAND)
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Message handler code here
    await context.bot.copy_message(
        chat_id=update.effective_chat.id,
        from_chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id
    )

if __name__ == '__main__':
    application.add_handler(CallbackQueryHandler(verify_anonymous_admin, pattern=r"^anon."))
    application.run_polling()
```