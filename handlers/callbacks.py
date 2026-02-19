"""Callback query handlers for inline buttons."""
import logging
import os
from telegram import Update, constants, InputMediaPhoto
from telegram.ext import ContextTypes
from handlers.navigation import (
    build_keyboard_for_entry,
    get_message_content,
    extract_entry_id_from_callback,
)
from data_manager import DataManager
from stats_manager import StatsManager
import config

logger = logging.getLogger(__name__)


async def _render_entry(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    keyboard,
    image_path: str | None,
) -> None:
    """Render entry content as text or photo, replacing message when media type changes."""
    query = update.callback_query
    message = query.message

    absolute_image_path = None
    if image_path and image_path != 'null':
        candidate_path = config.IMAGES_DIR / image_path
        if os.path.exists(candidate_path):
            absolute_image_path = candidate_path

    if absolute_image_path:
        if message and message.photo:
            with open(absolute_image_path, 'rb') as image_file:
                await query.edit_message_media(
                    media=InputMediaPhoto(
                        media=image_file,
                        caption=text,
                        parse_mode=constants.ParseMode.MARKDOWN,
                    ),
                    reply_markup=keyboard,
                )
            return

        if message:
            try:
                await message.delete()
            except Exception:
                logger.warning("Failed to delete previous text message before sending photo", exc_info=True)

        with open(absolute_image_path, 'rb') as image_file:
            await context.bot.send_photo(
                chat_id=message.chat_id,
                photo=image_file,
                caption=text,
                reply_markup=keyboard,
                parse_mode=constants.ParseMode.MARKDOWN,
            )
        return

    if message and message.photo:
        try:
            await message.delete()
        except Exception:
            logger.warning("Failed to delete previous photo message before sending text", exc_info=True)
        await context.bot.send_message(
            chat_id=message.chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=constants.ParseMode.MARKDOWN,
        )
        return

    await query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=constants.ParseMode.MARKDOWN,
    )


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
                text=text,
                reply_markup=keyboard,
                parse_mode=constants.ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text("❌ Помилка завантаження даних. Спробуйте /start")
        return

    # Get content and keyboard
    text, image_path = get_message_content(data_manager, entry_id)
    keyboard = build_keyboard_for_entry(data_manager, entry_id)

    try:
        await _render_entry(update, context, text, keyboard, image_path)

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
