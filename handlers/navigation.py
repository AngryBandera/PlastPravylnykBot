"""Navigation utilities for menu handling."""
import logging
from typing import List, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from data_manager import DataManager
import config

logger = logging.getLogger(__name__)


def build_keyboard_for_entry(data_manager: DataManager, entry_id: str) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for an entry.

    Args:
        data_manager: The DataManager instance
        entry_id: The entry ID to build keyboard for

    Returns:
        InlineKeyboardMarkup with buttons for this entry
    """
    entry = data_manager.get_entry(entry_id)
    if not entry:
        return InlineKeyboardMarkup([])

    buttons = []

    # Build buttons for any children, regardless of content_type
    children = data_manager.get_children_entries(entry_id)
    for child in children:
        callback_data = f"{config.CALLBACK_PREFIX_TOPIC}{child['id']}"
        buttons.append([
            InlineKeyboardButton(
                text=child['title'],
                callback_data=callback_data
            )
        ])

    # Add back button if not at root
    if entry_id != 'main':
        parent_id = entry['parent_id']
        if parent_id and parent_id != 'null':
            back_callback = f"{config.CALLBACK_PREFIX_BACK}{parent_id}"
            buttons.append([
                InlineKeyboardButton(
                    text=config.BACK_BUTTON_TEXT,
                    callback_data=back_callback
                )
            ])

        # Option to go back to main menu
        buttons.append([
            InlineKeyboardButton(
                text=config.MAIN_MENU_TEXT,
                callback_data=f"{config.CALLBACK_PREFIX_BACK}main"
            )
        ])

    return InlineKeyboardMarkup(buttons)


def get_message_content(data_manager: DataManager, entry_id: str) -> Tuple[str, str]:
    """
    Get text content and image path for an entry.

    Args:
        data_manager: The DataManager instance
        entry_id: The entry ID to get content for

    Returns:
        Tuple of (text_content, image_path_or_none)
    """
    entry = data_manager.get_entry(entry_id)
    if not entry:
        return "Інформацію не знайдено.", None

    text = entry['title']
    
    # Add content if it's text content
    if entry['content_type'] == 'text' and entry['content']:
        text += f"\n\n{entry['content']}"
    elif entry['content_type'] == 'menu':
        # For menu, show title only
        children = data_manager.get_children_entries(entry_id)
        if children:
            text += f"\n\nДоступно {len(children)} разділів"

    image_path = entry['image_url']

    return text, image_path


def extract_entry_id_from_callback(callback_data: str, prefix: str) -> str:
    """
    Extract entry ID from callback data.

    Args:
        callback_data: The full callback data string
        prefix: The prefix to remove (e.g., 'topic_')

    Returns:
        The extracted entry ID
    """
    return callback_data[len(prefix):] if callback_data.startswith(prefix) else ''
