from typing import Type, List, Callable

from telegram import Bot, Update, User, TelegramError
from telegram.ext import CommandHandler, MessageHandler, Filters, Handler, CallbackQueryHandler
from django_telegrambot.apps import DjangoTelegramBot

import logging


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def echo(bot, update):
    bot.sendMessage(update.message.chat_id, text=update.message.text)


class MyBot:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.info('Loading handlers for telegram bot')

        self.dispatcher = DjangoTelegramBot.dispatcher
        self.updater = DjangoTelegramBot.updater

        self.add_command(func=self.error, is_error=True)

    def error(self, bot: Bot, update: Update, error: TelegramError):
        self.logger.warning(f'Update "{update}" caused error "{error}"')

    def me(self) -> User:
        return self.updater.bot.get_me()

    def add_command(self, handler: Type[Handler] or Handler = None, names: str or List[str] = None,
                    func: Callable = None, is_error: bool = False, **kwargs):
        if is_error and not func:
            self.logger.fatal('You must give func if you add an error handler.')
            exit(1)
        elif is_error and func:
            if handler or names or kwargs:
                self.logger.warning('When adding an error handler all arguments except func will be ignored.')
            self.dispatcher.add_error_handler(func)
            return

        handler = handler or CommandHandler

        if isinstance(handler, Handler):
            self.dispatcher.add_handler(handler=handler)
        elif handler == MessageHandler:
            self.dispatcher.add_handler(handler=handler(kwargs.get('filters', Filters.all), func))
        elif handler == CallbackQueryHandler:
            self.dispatcher.add_handler(handler=handler(func, **kwargs))
        else:
            if not names:
                names = [func.__name__]
            elif not isinstance(names, List):
                names = [names]

            for name in names:
                self.dispatcher.add_handler(handler=handler(name, func, **kwargs))


my_bot: MyBot = None


def main():
    global my_bot
    my_bot = MyBot()
    from . import commands
