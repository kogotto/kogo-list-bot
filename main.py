#!./bot-venv/bin/python3

import logging
from uuid import uuid4
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InputChecklist,
    InputChecklistTask,
)
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
)
import mydb


LIST_GROUP_ID = -1001446356234


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)


def load_secrets() -> None:
    from dotenv import load_dotenv
    load_dotenv()
load_secrets()


def read_secret(name: str) -> str:
    import os
    secret = os.getenv(name)
    if not secret:
        raise Exception(f'There is no {name} in env. See .env.example')
    return secret


def read_token() -> str:
    return read_secret('KOGO_LIST_BOT_API_TOKEN')


def read_db_password() -> str:
    return read_secret('KOGO_LIST_BOT_DB_PASSWORD')


db = mydb.MyDB(read_db_password())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Hi')


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input = update.message.text.split('\n')
    await db.insert_goods(input, update.effective_user.name)


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ' '.join(context.args).upper()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
    )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goods = await db.get_actual_goods()
    print(goods)
    checklist = InputChecklist(
        title='Checklist title by kogo_list_bot',
        tasks=[
            InputChecklistTask(
                id=i,
                text=good[0],
            ) for (i, good) in enumerate(goods)
        ]
    )
    await context.bot.send_checklist(
        business_connection_id='asdf',
        chat_id=update.effective_chat.id,
        checklist=checklist,
    )


async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
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
    application = ApplicationBuilder().token(read_token()).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    caps_handler = CommandHandler('caps', caps)
    application.add_handler(caps_handler)

    list_handler = CommandHandler('list', list_command)
    application.add_handler(list_handler)

    process_message_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND) & filters.Chat(LIST_GROUP_ID),
        process_message
    )
    application.add_handler(process_message_handler)

    inline_caps_handler = InlineQueryHandler(inline_caps)
    application.add_handler(inline_caps_handler)

    # Keep this handler as low as possible
    unknown_command_handler = MessageHandler(filters.COMMAND, unknown_command)
    application.add_handler(unknown_command_handler)

    application.run_polling()
