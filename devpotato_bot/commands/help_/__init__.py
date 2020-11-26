import re
import typing
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, CallbackQuery
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler, CallbackQueryHandler

from . import _strings as strings


COMMAND_DESCRIPTION = "Show bot's abilities"


class Page(typing.NamedTuple):
    page_title: str
    page_contents: str
    page_id: str


class HelpPages:
    def __init__(self):
        self.data_prefix = 'help'
        self.ignored_button_data = 'NONE'
        self.start_page = Page(strings.PAGE_TITLE__HOME, strings.PAGE__HOME, 'home')
        self.page_layout = [[
            self.start_page,
            Page(strings.PAGE_TITLE__ROLL, strings.PAGE__ROLL, 'roll'),
            Page(strings.PAGE_TITLE__DAILY_TITLES, strings.PAGE__DAILY_TITLES, 'daily-titles'),
        ]]
        self.page_map: typing.Dict[str, Page] = {
            p.page_id: p
            for row in self.page_layout
            for p in row
        }

    def register_handlers(self, runner):
        dispatcher = runner.updater.dispatcher
        dispatcher.add_handler(CommandHandler("help", self._command_callback))
        runner.add_command_description('help', COMMAND_DESCRIPTION)

        page_ids = '|'.join(re.escape(page_id) for page_id in self.page_map)
        dispatcher.add_handler(CallbackQueryHandler(
            self._button_callback,
            pattern=f'^{self.data_prefix}:({page_ids}|{self.ignored_button_data})$',
        ))

    def _command_callback(self, update: Update, _context: CallbackContext):
        """Send a message when the command /help is issued."""
        update.message.reply_markdown_v2(**self._format_page(self.start_page))

    def _button_callback(self, update: Update, context: CallbackContext):
        """Switch help page."""
        query: CallbackQuery = update.callback_query
        callback_query: CallbackQuery = update.callback_query
        if context.match[1] == self.ignored_button_data:
            return
        requested_page = self.page_map.get(context.match[1])
        if requested_page is None:
            return
        callback_query.edit_message_text(**self._format_page(requested_page))

    def _format_page(self, current_page: Page):
        buttons = [
            [self._get_page_button(p, current_page) for p in button_row]
            for button_row in self.page_layout
        ]
        return dict(text=current_page.page_contents,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=ParseMode.MARKDOWN_V2)

    def _get_page_button(self, p: Page, disabled_page: Page):
        if p == disabled_page:
            suffix = self.ignored_button_data
        else:
            suffix = p.page_id
        return InlineKeyboardButton(p.page_title,
                                    callback_data=f'{self.data_prefix}:{suffix}')
