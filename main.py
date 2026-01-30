"""Main bot application."""
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import config
from data_manager import DataManager
from stats_manager import StatsManager
from handlers.start import start
from handlers.callbacks import button_callback, reload_data
from handlers.admin import stats, stats_daily, stats_users

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """
    Initialize application after creation.

    Args:
        application: The application object
    """
    logger.info("Initializing bot...")
    
    # Load data from CSV
    data_manager = DataManager(config.CSV_FILE)
    if not data_manager.is_valid():
        logger.error("Failed to initialize data manager")
        raise RuntimeError("Failed to load data from CSV")
    
    # Initialize statistics manager
    stats_manager = StatsManager(config.STATS_FILE)
    
    # Store managers in bot_data for access in handlers
    application.bot_data['data_manager'] = data_manager
    application.bot_data['stats_manager'] = stats_manager
    logger.info("Data manager and stats manager initialized successfully")


def main():
    """Start the bot."""
    # Create application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Set up post init
    application.post_init = post_init
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("stats_daily", stats_daily))
    application.add_handler(CommandHandler("stats_users", stats_users))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=[
        "message",
        "callback_query",
        "edited_message",
    ])


if __name__ == '__main__':
    main()
