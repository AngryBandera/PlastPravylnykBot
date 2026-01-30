"""Callback query handlers for inline buttons."""
import logging
import os
from telegram import Update, constants
from telegram.ext import ContextTypes
from handlers.navigation import (
    build_keyboard_for_entry,
    get_message_content,
    extract_entry_id_from_callback
)
from data_manager import DataManager
from stats_manager import StatsManager
import config

logger = logging.getLogger(__name__)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle button callbacks.

    Args:
        update: The update object
        context: The context object
    """
    query = update.callback_query
    await query.answer()

    data_manager: DataManager = context.bot_data.get('data_manager')
    if not data_manager or not data_manager.is_valid():
        await query.edit_message_text("❌ Виникла помилка. Спробуйте пізніше.")
        return

    callback_data = query.data
    
    # Extract entry ID based on callback prefix
    if callback_data.startswith(config.CALLBACK_PREFIX_TOPIC):
        entry_id = extract_entry_id_from_callback(
            callback_data,
            config.CALLBACK_PREFIX_TOPIC
        )
    elif callback_data.startswith(config.CALLBACK_PREFIX_BACK):
        entry_id = extract_entry_id_from_callback(
            callback_data,
            config.CALLBACK_PREFIX_BACK
        )
    else:
        await query.edit_message_text("❌ Невідома команда.")
        return

    # Track statistics
    stats_manager: StatsManager = context.bot_data.get('stats_manager')
    if stats_manager:
        user = update.effective_user
        stats_manager.track_user(user.id, username=user.username, first_name=user.first_name)
        stats_manager.track_click(entry_id, user_id=user.id)

    # Get entry data
    entry = data_manager.get_entry(entry_id)
    if not entry:
        # Entry not found - redirect to main menu gracefully
        main_entry = data_manager.get_entry('main')
        if main_entry:
            text, _ = get_message_content(data_manager, 'main')
            keyboard = build_keyboard_for_entry(data_manager, 'main')
            await query.edit_message_text(
                f"ℹ️ Цей розділ більше не доступний.\n\n{text}",
                reply_markup=keyboard,
                parse_mode=constants.ParseMode.HTML
            )
        else:
            await query.edit_message_text("❌ Помилка завантаження даних. Спробуйте /start")
        return

    # Get content and keyboard
    text, image_path = get_message_content(data_manager, entry_id)
    keyboard = build_keyboard_for_entry(data_manager, entry_id)

    try:
        # Edit message with new content
        await query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=constants.ParseMode.HTML
        )
        
        # If there's an image, send it as a new message
        if image_path and image_path != 'null' and os.path.exists(config.IMAGES_DIR / image_path):
            try:
                with open(config.IMAGES_DIR / image_path, 'rb') as image_file:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=image_file,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode=constants.ParseMode.HTML
                    )
            except Exception as e:
                logger.error(f"Error sending image: {e}")
                
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        await query.edit_message_text(
            f"❌ Помилка при оновленні: {str(e)}"
        )


async def reload_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle reload data callback.

    Args:
        update: The update object
        context: The context object
    """
    query = update.callback_query
    await query.answer()

    data_manager: DataManager = context.bot_data.get('data_manager')
    if not data_manager:
        await query.edit_message_text("❌ Data manager не ініціалізований.")
        return

    if data_manager.reload():
        await query.edit_message_text(
            "✅ Дані успішно перезавантажені!"
        )
    else:
        await query.edit_message_text(
            "❌ Помилка при перезавантаженні даних."
        )
