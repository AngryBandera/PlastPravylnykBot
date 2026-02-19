"""Data manager module for loading and managing content from CSV file."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

logger = logging.getLogger(__name__)


def _normalize_multiline_text(value: Any) -> str:
    """Convert escaped newline sequences to real line breaks."""
    if pd.isna(value):
        return ''
    return str(value).replace('\\n', '\n').strip()


class DataManager:
    """Manages loading and organizing content from CSV file."""

    def __init__(self, csv_path: Path):
        """
        Initialize DataManager.

        Args:
            csv_path: Path to the CSV file containing content
        """
        self.csv_path = csv_path
        self.data: Dict[str, Dict[str, Any]] = {}
        self.children_map: Dict[str, List[str]] = {}
        self.load_data()

    def load_data(self) -> bool:
        """
        Load and parse CSV file into memory.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.csv_path.exists():
            logger.error(f"CSV file not found: {self.csv_path}")
            return False

        try:
            df = pd.read_csv(self.csv_path)
            
            # Validate required columns
            required_cols = {'id', 'parent_id', 'title', 'content_type', 'content', 'has_subtopics'}
            if not required_cols.issubset(df.columns):
                logger.error(f"CSV missing required columns. Required: {required_cols}")
                return False

            # Backward compatibility: allow CSV without image_url column
            if 'image_url' not in df.columns:
                logger.warning("CSV does not contain 'image_url' column. Defaulting image_url to None for all entries.")
                df['image_url'] = None

            # Reset data structures
            self.data = {}
            self.children_map = {}

            # Process each row
            for _, row in df.iterrows():
                entry_id = str(row['id']).strip()
                parent_id = str(row['parent_id']).strip() if pd.notna(row['parent_id']) else None

                # Store entry data
                self.data[entry_id] = {
                    'id': entry_id,
                    'parent_id': parent_id,
                    'title': str(row['title']).strip(),
                    'content_type': str(row['content_type']).strip(),
                    'content': _normalize_multiline_text(row['content']),
                    'image_url': str(row['image_url']).strip() if pd.notna(row['image_url']) else None,
                    'has_subtopics': str(row['has_subtopics']).lower() == 'true',
                }

                # Build children map
                if parent_id and parent_id != 'null':
                    if parent_id not in self.children_map:
                        self.children_map[parent_id] = []
                    self.children_map[parent_id].append(entry_id)

            logger.info(f"Successfully loaded {len(self.data)} entries from CSV")
            self._validate_data()
            return True

        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            return False

    def _validate_data(self) -> None:
        """Validate data integrity (warn about orphaned entries, etc)."""
        for entry_id, entry in self.data.items():
            parent_id = entry['parent_id']
            
            # Check if parent exists
            if parent_id and parent_id not in self.data:
                logger.warning(f"Entry '{entry_id}' has non-existent parent '{parent_id}'")

    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Get entry data by ID.

        Args:
            entry_id: The ID of the entry to retrieve

        Returns:
            Entry data dictionary or None if not found
        """
        return self.data.get(entry_id)

    def get_children(self, parent_id: str) -> List[str]:
        """
        Get list of child entry IDs for a given parent.

        Args:
            parent_id: The parent entry ID

        Returns:
            List of child entry IDs
        """
        return self.children_map.get(parent_id, [])

    def get_children_entries(self, parent_id: str) -> List[Dict[str, Any]]:
        """
        Get full entry data for all children of a parent.

        Args:
            parent_id: The parent entry ID

        Returns:
            List of child entry dictionaries
        """
        child_ids = self.get_children(parent_id)
        return [self.data[cid] for cid in child_ids if cid in self.data]

    def get_root_entries(self) -> List[Dict[str, Any]]:
        """
        Get all root level entries (those with parent_id = null).

        Returns:
            List of root entry dictionaries
        """
        return self.get_children_entries('main')

    def get_breadcrumb_path(self, entry_id: str) -> List[Dict[str, Any]]:
        """
        Get the full path from root to the given entry.

        Args:
            entry_id: The entry to get path for

        Returns:
            List of entries from root to target, inclusive
        """
        path = []
        current_id = entry_id

        while current_id:
            entry = self.get_entry(current_id)
            if not entry:
                break
            path.insert(0, entry)
            current_id = entry['parent_id']

        return path

    def reload(self) -> bool:
        """
        Reload data from CSV file (useful for hot reloading).

        Returns:
            True if reload successful, False otherwise
        """
        logger.info("Reloading data from CSV...")
        return self.load_data()

    def is_valid(self) -> bool:
        """Check if data was loaded successfully."""
        return len(self.data) > 0
