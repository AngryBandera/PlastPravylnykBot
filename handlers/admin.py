"""Admin command handlers."""
import logging
from telegram import Update, constants
from telegram.ext import ContextTypes
from stats_manager import StatsManager

logger = logging.getLogger(__name__)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show bot statistics.

    Args:
        update: The update object
        context: The context object
    """
    stats_manager: StatsManager = context.bot_data.get('stats_manager')
    if not stats_manager:
        await update.message.reply_text("❌ Статистика недоступна.")
        return

    # Get stats summary
    summary = stats_manager.get_stats_summary()
    top_entries = summary['top_entries']
    commands = summary['commands_used']

    # Build statistics message
    text = "📊 <b>Статистика бота</b>\n\n"
    
    text += "👥 <b>Користувачі:</b>\n"
    text += f"  • Всього: {summary['total_users']}\n"
    text += f"  • Активні (7 днів): {summary['active_users_7d']}\n"
    text += f"  • Активні (30 днів): {summary['active_users_30d']}\n\n"
    
    text += f"🖱 <b>Кліки:</b> {summary['total_clicks']}\n\n"
    
    if top_entries:
        text += "🔝 <b>Популярні розділи:</b>\n"
        for entry_id, count in top_entries:
            text += f"  • {entry_id}: {count} кліків\n"
        text += "\n"
    
    if commands:
        text += "⌨️ <b>Команди:</b>\n"
        for cmd, count in sorted(commands.items(), key=lambda x: x[1], reverse=True):
            text += f"  • /{cmd}: {count}\n"
        text += "\n"
    
    text += f"📅 Створено: {summary['created_at'][:10]}\n"
    text += f"🔄 Оновлено: {summary['last_updated'][:19].replace('T', ' ')}"

    await update.message.reply_text(
        text=text,
        parse_mode=constants.ParseMode.HTML
    )


async def stats_daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show daily statistics for the last week.

    Args:
        update: The update object
        context: The context object
    """
    stats_manager: StatsManager = context.bot_data.get('stats_manager')
    if not stats_manager:
        await update.message.reply_text("❌ Статистика недоступна.")
        return

    # Get daily stats
    daily = stats_manager.get_daily_stats(7)

    text = "📅 <b>Денна статистика (останні 7 днів)</b>\n\n"
    
    for date in sorted(daily.keys(), reverse=True):
        day_data = daily[date]
        text += f"<b>{date}</b>\n"
        text += f"  👥 Користувачів: {day_data['unique_users']}\n"
        text += f"  🖱 Кліків: {day_data['clicks']}\n\n"

    await update.message.reply_text(
        text=text,
        parse_mode=constants.ParseMode.HTML
    )


async def stats_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show user list with details.

    Args:
        update: The update object
        context: The context object
    """
    stats_manager: StatsManager = context.bot_data.get('stats_manager')
    if not stats_manager:
        await update.message.reply_text("❌ Статистика недоступна.")
        return

    users = stats_manager.stats['users']
    
    if not users:
        await update.message.reply_text("Ще немає користувачів.")
        return

    text = f"👥 <b>Користувачі ({len(users)})</b>\n\n"
    
    # Sort by last seen (most recent first)
    sorted_users = sorted(
        users.items(),
        key=lambda x: x[1]['last_seen'],
        reverse=True
    )
    
    for user_id, user_data in sorted_users[:20]:  # Show max 20 users
        username = user_data.get('username', 'N/A')
        first_name = user_data.get('first_name', 'N/A')
        interactions = user_data.get('interactions', 0)
        last_seen = user_data['last_seen'][:10]
        
        text += f"<b>{first_name}</b> (@{username})\n"
        text += f"  ID: {user_id}\n"
        text += f"  Взаємодій: {interactions}\n"
        text += f"  Останній візит: {last_seen}\n\n"
    
    if len(users) > 20:
        text += f"... і ще {len(users) - 20} користувачів"

    await update.message.reply_text(
        text=text,
        parse_mode=constants.ParseMode.HTML
    )
