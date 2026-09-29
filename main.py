#!/usr/bin/env python3

import asyncpg
import logging
from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    filters,
    Application,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
)
import mydb
import secrets_config


DONE_CALLBACK_DATA = 'done'


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)


async def create_pool():
    db_config = secrets_config.read_db_config()
    return await asyncpg.create_pool(**db_config)


async def post_init(application: Application):
    pool = await create_pool()
    application.bot_data['db'] = mydb.MyDB(pool)
    application.bot_data['pool'] = pool

    commands = [
        BotCommand(
            command='list',
            description='Get actual goods list',
        )
    ]
    await application.bot.set_my_commands(commands)


async def post_shutdown(application: Application):
    pool = application.bot_data.get('pool')
    if pool:
        await pool.close()


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    input = [
        good.strip() for good in update.message.text.split('\n') if good.strip()
    ]

    try:
        db = context.bot_data['db']
        await db.insert_goods(input, update.effective_user.name)
    except Exception as e:
        logging.error(e)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='❌ Что-то пошло не так. Повторите через некоторое время.',
        )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        db = context.bot_data['db']
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

    if update.effective_chat.id != secrets_config.read_my_group_id():
        return
    if query.data == DONE_CALLBACK_DATA:
        return

    try:
        db = context.bot_data['db']
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


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Не знаю такую комманду',
    )


if __name__ == '__main__':
    secrets_config.load()

    application = (
        ApplicationBuilder()
        .token(secrets_config.read_token())
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    MY_GROUP = filters.Chat(secrets_config.read_my_group_id())

    list_handler = CommandHandler('list', list_command, filters=MY_GROUP)
    application.add_handler(list_handler)

    callback_handler = CallbackQueryHandler(list_callback)
    application.add_handler(callback_handler)

    process_message_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND) & MY_GROUP,
        process_message
    )
    application.add_handler(process_message_handler)

    # Keep this handler as low as possible
    unknown_command_handler = MessageHandler(MY_GROUP & filters.COMMAND, unknown_command)
    application.add_handler(unknown_command_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
