"""Statistics manager for tracking bot usage."""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class StatsManager:
    """Manages bot usage statistics."""

    def __init__(self, stats_file: Path):
        """
        Initialize StatsManager.

        Args:
            stats_file: Path to the JSON file for storing stats
        """
        self.stats_file = stats_file
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading stats: {e}")
                return self._default_stats()
        return self._default_stats()

    def _default_stats(self) -> Dict[str, Any]:
        """Return default stats structure."""
        return {
            'users': {},  # user_id: {first_seen, last_seen, username, first_name}
            'clicks': {},  # entry_id: count
            'total_clicks': 0,
            'commands': defaultdict(int),  # command: count
            'daily_stats': {},  # date: {users: set, clicks: count}
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }

    def _save_stats(self) -> bool:
        """Save statistics to file."""
        try:
            self.stats['last_updated'] = datetime.now().isoformat()
            # Convert sets to lists for JSON serialization
            stats_copy = json.loads(json.dumps(self.stats, default=list))
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_copy, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
            return False

    def track_user(self, user_id: int, username: str = None, first_name: str = None) -> None:
        """
        Track a user interaction.

        Args:
            user_id: The Telegram user ID
            username: The user's username (optional)
            first_name: The user's first name (optional)
        """
        user_id_str = str(user_id)
        current_time = datetime.now().isoformat()

        if user_id_str not in self.stats['users']:
            self.stats['users'][user_id_str] = {
                'first_seen': current_time,
                'last_seen': current_time,
                'username': username,
                'first_name': first_name,
                'interactions': 0
            }
        else:
            self.stats['users'][user_id_str]['last_seen'] = current_time
            if username:
                self.stats['users'][user_id_str]['username'] = username
            if first_name:
                self.stats['users'][user_id_str]['first_name'] = first_name

        self.stats['users'][user_id_str]['interactions'] += 1
        self._save_stats()

    def track_click(self, entry_id: str, user_id: int = None) -> None:
        """
        Track a button click.

        Args:
            entry_id: The ID of the entry that was clicked
            user_id: The user who clicked (optional)
        """
        if entry_id not in self.stats['clicks']:
            self.stats['clicks'][entry_id] = 0
        
        self.stats['clicks'][entry_id] += 1
        self.stats['total_clicks'] += 1

        # Track daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats['daily_stats']:
            self.stats['daily_stats'][today] = {
                'users': [],
                'clicks': 0
            }
        
        self.stats['daily_stats'][today]['clicks'] += 1
        if user_id:
            user_list = self.stats['daily_stats'][today]['users']
            if str(user_id) not in user_list:
                user_list.append(str(user_id))

        self._save_stats()

    def track_command(self, command: str) -> None:
        """
        Track a command usage.

        Args:
            command: The command that was used (e.g., 'start', 'stats')
        """
        if 'commands' not in self.stats:
            self.stats['commands'] = {}
        
        if command not in self.stats['commands']:
            self.stats['commands'][command] = 0
        
        self.stats['commands'][command] += 1
        self._save_stats()

    def get_total_users(self) -> int:
        """Get total number of unique users."""
        return len(self.stats['users'])

    def get_active_users(self, days: int = 7) -> int:
        """
        Get number of active users in the last N days.

        Args:
            days: Number of days to look back

        Returns:
            Count of active users
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        active = 0
        for user_data in self.stats['users'].values():
            last_seen = datetime.fromisoformat(user_data['last_seen'])
            if last_seen >= cutoff:
                active += 1
        
        return active

    def get_top_entries(self, limit: int = 10) -> List[tuple]:
        """
        Get most clicked entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of tuples (entry_id, click_count)
        """
        sorted_clicks = sorted(
            self.stats['clicks'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_clicks[:limit]

    def get_stats_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all statistics.

        Returns:
            Dictionary with summary statistics
        """
        return {
            'total_users': self.get_total_users(),
            'active_users_7d': self.get_active_users(7),
            'active_users_30d': self.get_active_users(30),
            'total_clicks': self.stats['total_clicks'],
            'top_entries': self.get_top_entries(5),
            'commands_used': dict(self.stats.get('commands', {})),
            'created_at': self.stats['created_at'],
            'last_updated': self.stats['last_updated']
        }

    def get_daily_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get daily statistics for the last N days.

        Args:
            days: Number of days to include

        Returns:
            Dictionary with daily stats
        """
        from datetime import timedelta
        
        result = {}
        today = datetime.now()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            if date in self.stats['daily_stats']:
                day_data = self.stats['daily_stats'][date]
                result[date] = {
                    'unique_users': len(day_data.get('users', [])),
                    'clicks': day_data.get('clicks', 0)
                }
            else:
                result[date] = {
                    'unique_users': 0,
                    'clicks': 0
                }
        
        return result
