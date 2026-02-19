"""Start command handler."""
import logging
from telegram import Update, constants
from telegram.ext import ContextTypes
from handlers.navigation import build_keyboard_for_entry, get_message_content
from data_manager import DataManager
from stats_manager import StatsManager

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command.

    Args:
        update: The update object
        context: The context object with data_manager in context.bot_data
    """
    data_manager: DataManager = context.bot_data.get('data_manager')
    if not data_manager or not data_manager.is_valid():
        await update.message.reply_text(
            "❌ Виникла помилка при завантаженні даних. Спробуйте пізніше."
        )
        return

    # Track statistics
    stats_manager: StatsManager = context.bot_data.get('stats_manager')
    if stats_manager:
        user = update.effective_user
        stats_manager.track_user(
            user.id,
            username=user.username,
            first_name=user.first_name
        )
        stats_manager.track_command('start')

    # Get main entry
    entry_id = 'main'
    text, image_path = get_message_content(data_manager, entry_id)
    keyboard = build_keyboard_for_entry(data_manager, entry_id)

    # Send message with keyboard
    await update.message.reply_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=constants.ParseMode.MARKDOWN
    )
