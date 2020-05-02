import telegram.ext
from telegram import Update
from telegram.ext import CallbackContext


class ExtraContextMixin:
    def __init__(self, *args, **kwargs):
        self.extra_context = kwargs.pop('extra_context', dict())
        super().__init__(*args, **kwargs)

    def handle_update(self, update: Update, dispatcher, check_result, context: CallbackContext = None):
        assert context is not None
        context.update(self.extra_context)
        return super().handle_update(update, dispatcher, check_result, context)


class CommandHandler(ExtraContextMixin, telegram.ext.CommandHandler):
    pass


class MessageHandler(ExtraContextMixin, telegram.ext.MessageHandler):
    pass


class CallbackQueryHandler(ExtraContextMixin, telegram.ext.CallbackQueryHandler):
    pass
