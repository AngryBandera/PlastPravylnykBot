# Statistics Guide

## Available Commands

### 📊 `/stats` - Overall Statistics
Get a comprehensive overview of bot usage:
```
📊 Статистика бота

👥 Користувачі:
  • Всього: 15
  • Активні (7 днів): 8
  • Активні (30 днів): 12

🖱 Кліки: 234

🔝 Популярні розділи:
  • history: 45 кліків
  • principles: 38 кліків
  • ranks: 32 кліків

⌨️ Команди:
  • /start: 15
  • /stats: 3
```

### 📅 `/stats_daily` - Daily Breakdown
See daily activity for the last 7 days:
```
📅 Денна статистика (останні 7 днів)

2026-01-31
  👥 Користувачів: 5
  🖱 Кліків: 34

2026-01-30
  👥 Користувачів: 8
  🖱 Кліків: 52
```

### 👥 `/stats_users` - User Details
View list of users who interacted with the bot:
```
👥 Користувачі (15)

Ivan Petrov (@ivanpetrov)
  ID: 123456789
  Взаємодій: 23
  Останній візит: 2026-01-31

Maria Kovalenko (@maria_k)
  ID: 987654321
  Взаємодій: 18
  Останній візит: 2026-01-30
```

## What Gets Tracked

### Automatically Tracked:
✅ **Users**
- User ID, username, first name
- First interaction date
- Last interaction date
- Total number of interactions

✅ **Button Clicks**
- Which sections/pages users click
- Total click count per section
- Overall click count

✅ **Commands**
- Which commands users run
- Frequency of each command

✅ **Daily Activity**
- Unique users per day
- Clicks per day
- 7-day history

### Data Storage
- **Location**: `data/stats.json`
- **Format**: JSON (human-readable)
- **Persistence**: Data survives bot restarts
- **Privacy**: Stored locally, not sent anywhere

## Data Structure

Example `stats.json`:
```json
{
  "users": {
    "123456789": {
      "first_seen": "2026-01-25T10:30:00",
      "last_seen": "2026-01-31T14:20:00",
      "username": "john_doe",
      "first_name": "John",
      "interactions": 15
    }
  },
  "clicks": {
    "history": 45,
    "principles": 38,
    "ranks": 32
  },
  "total_clicks": 234,
  "commands": {
    "start": 15,
    "stats": 3
  },
  "daily_stats": {
    "2026-01-31": {
      "users": ["123456789", "987654321"],
      "clicks": 34
    }
  }
}
```

## Privacy & Security

### User Data
- Only collects public Telegram data (username, first name)
- No message content is stored
- No personal conversations tracked
- User IDs are numeric (not revealing)

### Access Control
**Current**: Statistics commands work for everyone

**Recommended for production**: Add admin-only restriction:
```python
ADMIN_IDS = [123456789]  # Your Telegram ID

async def stats(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Доступ заборонено")
        return
    # ... rest of code
```

Get your Telegram ID by messaging [@userinfobot](https://t.me/userinfobot)

## Exporting Data

### Manual Export
The `stats.json` file can be:
- Opened in any text editor
- Imported into Excel/Google Sheets (convert to CSV)
- Analyzed with Python scripts
- Backed up regularly

### Automated Backup
Add to your server cron:
```bash
# Backup stats daily at 2 AM
0 2 * * * cp /path/to/PlastPravylnykBot/data/stats.json /backups/stats_$(date +\%Y\%m\%d).json
```

## Statistics Best Practices

### For Growth Analysis
- Check `/stats_daily` weekly to spot trends
- Compare 7-day vs 30-day active users
- Identify most popular content with top entries

### For Content Improvement
- Low clicks = topic may need better naming/positioning
- High clicks = users find it valuable
- Use data to decide which sections to expand

### For User Retention
- Track active users over time
- If dropping, consider new content
- Regular updates keep users coming back

## Troubleshooting

**Stats not updating:**
- Check `data/stats.json` exists and is writable
- Verify bot has permission to write to `data/` folder
- Check logs for save errors

**Stats showing zeros:**
- Need at least one user interaction after bot update
- Send `/start` to the bot to generate first data

**File too large:**
- Consider archiving old daily stats
- Implement data rotation (keep last 90 days)
- Current file typically < 100KB for hundreds of users
