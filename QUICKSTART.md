# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Python packages
```bash
pip install -r requirements.txt
```

### Step 2: Set up environment
```bash
cp .env.example .env
# Edit .env and paste your bot token from BotFather
```

### Step 3: Run the bot
```bash
python main.py
```

## Testing the Bot

1. Start bot: `/start`
2. Click any topic button
3. Navigate through menus
4. Use ← Назад button to go back

## Editing Content

### Quick Edit
1. Open `data/content.csv` in Excel or Google Sheets
2. Add/edit rows:
   - Each row = one menu item or page
   - Set `parent_id` to show under parent menu
   - Use `content_type: menu` for submenus
3. Save file
4. Restart bot (auto-loads on next /start)

### Example: Add New Section

Add this row to CSV:
```
animals,main,🦁 Animals,menu,null,null,true
animals_lion,animals,Lion,text,The lion is a big cat,null,false
animals_tiger,animals,Tiger,text,The tiger has stripes,null,false
```

Result: New "🦁 Animals" button appears in main menu with Lion and Tiger options.

## Structure Cheat Sheet

**CSV Columns:**
- `id` - unique name (no spaces)
- `parent_id` - parent's id (or null for main)
- `title` - button text
- `content_type` - menu/text/image
- `content` - text to show
- `image_url` - image filename
- `has_subtopics` - true/false

**ID Naming Convention:**
- Use lowercase with underscores: `topic_name`
- Use hierarchy in names: `topic_subtopic_item`

## File Locations

- **Bot code**: `main.py`
- **Content**: `data/content.csv`
- **Images**: `images/` folder
- **Config**: `config.py`
