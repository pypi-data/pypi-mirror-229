from telegram.ext import (ApplicationBuilder,
                          CommandHandler, MessageHandler, filters)
from utils import image, reply, instructions
import openai

__all__ = ['create_app', 'add_handlers']


def create_app(bot_token, openai_token):
    openai.api_key = openai_token
    new_application = (
        ApplicationBuilder()
        .token(bot_token)
        .build()
    )
    return new_application


def add_handlers(application):
    application.add_handler(CommandHandler('start', instructions))
    application.add_handler(CommandHandler('image', image))
    application.add_handler(CommandHandler('text', reply))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, instructions))
