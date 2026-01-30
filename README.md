# Plast Pravylnyk Telegram Bot

Telegram bot for learning about the Plast organization and its rules (Pravylnyk).

## Features

- 📚 Hierarchical menu system with topics and subtopics
- 🖼️ Support for text and image content
- 📋 Easy content management via CSV file
- 🔄 Dynamic menu generation from data
- 🌐 Full Ukrainian language support
- 📊 Built-in usage statistics and analytics

## Project Structure

```
PlastPravylnykBot/
├── main.py                 # Bot entry point
├── config.py              # Configuration and constants
├── data_manager.py        # CSV loader and data manager
├── stats_manager.py       # Statistics tracking and storage
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── .gitignore
├── data/
│   ├── content.csv       # Content data file
│   └── stats.json        # Statistics data (auto-generated)
├── images/               # Image files referenced in CSV
└── handlers/
    ├── __init__.py
    ├── start.py          # /start command handler
    ├── callbacks.py      # Button callback handlers
    ├── navigation.py     # Menu navigation utilities
    └── admin.py          # Admin commands (stats)
```

## Setup Instructions

### 1. Clone or Download

```bash
cd /path/to/PlastPravylnykBot
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Bot Token

1. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Get your bot token from [BotFather](https://t.me/BotFather) on Telegram

3. Update `.env`:
   ```
   BOT_TOKEN=your_actual_token_here
   ```

### 5. Run the Bot

```bash
python main.py
```

## Managing Content

### CSV File Format

Edit `data/content.csv` to manage content. Required columns:

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Unique identifier | `main`, `history`, `history_founding` |
| `parent_id` | Parent menu ID (null for root) | `main`, `history` |
| `title` | Button/menu title | `📚 Історія` |
| `content_type` | Type of content: `menu`, `text`, `image` | `menu` |
| `content` | Text content (for text type) | `ПЛАСТ було засновано...` |
| `image_url` | Image filename (for image type) | `image1.jpg` |
| `has_subtopics` | Boolean (true/false) | `true` |

### Example Structure

```csv
id,parent_id,title,content_type,content,image_url,has_subtopics
main,null,Welcome,text,Welcome message,null,false
history,main,📚 History,menu,null,null,true
history_founding,history,Founding,text,Text about founding,null,false
history_image,history,Historical Photo,image,null,photo.jpg,false
```

### Hierarchy Rules

- Root entries must have `parent_id = null`
- All other entries reference their parent via `parent_id`
- Menu entries (`content_type = menu`) automatically show child buttons
- Text entries can have content and optional images

### Adding Images

1. Place image files in `images/` directory
2. Reference filename in CSV's `image_url` column
3. Images can be JPG, PNG, etc.

## How It Works

1. **Bot starts** → `/start` command displays main menu
2. **User clicks button** → Callback triggers navigation
3. **Data lookup** → DataManager retrieves entry from CSV data
4. **Content display** → Text content and/or image shown with new menu
5. **Navigation** → Back buttons appear for non-root menus

## CSV Auto-Reload

To reload content without restarting the bot, you can implement an admin command. Modify the code to add:

```python
@app.command()
async def reload(update, context):
    data_manager = context.bot_data['data_manager']
    if data_manager.reload():
        await update.message.reply_text("✅ Data reloaded")
```

## Statistics Commands

The bot tracks usage statistics automatically. Available commands:

### `/stats` - General Statistics
Shows overall bot usage:
- Total users (all-time, 7-day, 30-day active)
- Total clicks
- Most popular sections
- Command usage

### `/stats_daily` - Daily Statistics
Shows daily breakdown for the last 7 days:
- Unique users per day
- Clicks per day

### `/stats_users` - User List
Shows detailed user information:
- Username and first name
- Total interactions
- Last visit date

**Data Storage**: Statistics are stored in `data/stats.json` and persist across bot restarts.

## Customization

### Styling
- Emoji in titles: Add directly to CSV title column
- Text formatting: Use HTML in content (if implemented)
- Button layout: Edit `BUTTONS_PER_ROW` in `config.py`

### Translations
- Change text in CSV to any language
- Update button names in `config.py` (BACK_BUTTON_TEXT, MAIN_MENU_TEXT)

### Future Enhancements
- Pagination for large menus
- Search functionality
- User preferences storage
- Multilingual support
- Export statistics to CSV/Excel

## Troubleshooting

**Bot doesn't start:**
- Check BOT_TOKEN is set in `.env`
- Verify `data/content.csv` exists and is readable
- Check log output for specific errors

**CSV not loading:**
- Verify file encoding is UTF-8
- Check CSV format matches required columns
- Look for error messages in console

**Images not showing:**
- Verify image files exist in `images/` folder
- Check filename matches CSV's `image_url` column
- Ensure images are in supported format (JPG, PNG)

## License

See LICENSE file
