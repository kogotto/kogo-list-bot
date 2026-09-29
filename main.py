#!./bot-venv/bin/python3

import logging
from uuid import uuid4
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
)
import mydb


LIST_GROUP_ID = -1001446356234
DONE_CALLBACK_DATA = 'done'


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


def read_business_connection_id() -> str:
    return read_secret('KOGO_LIST_BOT_BUSINESS_CONNECTION_ID')


db = mydb.MyDB(read_db_password())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Hi')


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    input = update.message.text.split('\n')

    try:
        await db.insert_goods(input, update.effective_user.name)
    except Exception as e:
        logging.error(e)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='❌ Что-то пошло не так. Повторите через некоторое время.',
        )


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ' '.join(context.args).upper()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
    )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        goods = await db.get_actual_goods()
    except Exception as e:
        logging.error(e)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='❌ Что-то пошло не так. Повторите через некоторое время.',
        )
        return

    if not goods:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Actual goods list empty',
        )
        return

    keyboard_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                f'⬜ {good.name()}',
                callback_data=str(good.id()),
            )] for good in goods
        ]
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Actual goods list',
        reply_markup=keyboard_markup,
    )


def switch_to_done(text: str):
    return text.replace("⬜", "✅")


def disable_push_button(current_keyboard, pushed_id: str):
    result = []
    for current_row in current_keyboard:
        new_row = [
            InlineKeyboardButton(
                text=switch_to_done(button.text),
                callback_data=DONE_CALLBACK_DATA,
            ) if button.callback_data == pushed_id else button
            for button in current_row
        ]
        result.append(new_row)
    return result


async def list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == DONE_CALLBACK_DATA:
        return

    try:
        await db.buy_good(int(query.data))
    except Exception as e:
        logging.error(e)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='❌ Что-то пошло не так. Повторите через некоторое время.'
        )
        return

    current_keyboard = query.message.reply_markup.inline_keyboard
    new_keyboard_markup = disable_push_button(current_keyboard, query.data)
    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(new_keyboard_markup)
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

    callback_handler = CallbackQueryHandler(list_callback)
    application.add_handler(callback_handler)

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

    application.run_polling(allowed_updates=Update.ALL_TYPES)
