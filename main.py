#!./bot-venv/bin/python3

import logging
from uuid import uuid4
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
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
        text=message,
    )


async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    logging.warning(f'{query=}')
    if not query:
        return
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper()),
        ),
    ]
    await context.bot.answer_inline_query(update.inline_query.id, results)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Не знаю такую комманду',
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

    inline_caps_handler = InlineQueryHandler(inline_caps)
    application.add_handler(inline_caps_handler)

    # Keep this handler as low as possible
    unknown_command_handler = MessageHandler(filters.COMMAND, unknown_command)
    application.add_handler(unknown_command_handler)

    application.run_polling()
