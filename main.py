#!./bot-venv/bin/python3

import logging
from telegram import Update
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)


def read_token() -> str:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv('KOGO_LIST_BOT_API_TOKEN')
    if not token:
        raise Exception("There is no bot api token in env. See .env.example")
    return token


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Hi')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input = update.message.text
    message = f'Ты сказал "{input}"?'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ' '.join(context.args).upper()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


if __name__ == '__main__':
    token = read_token()
    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    caps_handler = CommandHandler('caps', caps)
    application.add_handler(caps_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    application.run_polling()
