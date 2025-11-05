"""
State management for resume capability
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


class StateManager:
    """Manages scraping state for resume capability"""

    def __init__(self, state_file: str = "state.json"):
        """
        Initialize state manager

        Args:
            state_file: Path to state file
        """
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """
        Load state from file

        Returns:
            State dictionary
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
                return {}
        return {}

    def save_state(self):
        """Save current state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save state file: {e}")

    def update_progress(
        self,
        action: str,
        channel_id: str,
        scraped_count: int,
        last_id: Optional[str] = None
    ):
        """
        Update scraping progress

        Args:
            action: Action being performed (scrapeMessages, scrapeChannelMembers)
            channel_id: Channel or guild ID
            scraped_count: Number of items scraped so far
            last_id: Last message/member ID processed
        """
        key = f"{action}_{channel_id}"
        self.state[key] = {
            "action": action,
            "channel_id": channel_id,
            "scraped_count": scraped_count,
            "last_id": last_id,
            "updated_at": datetime.now().isoformat()
        }
        self.save_state()

    def get_progress(self, action: str, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress for a specific action and channel

        Args:
            action: Action type
            channel_id: Channel or guild ID

        Returns:
            Progress dictionary or None
        """
        key = f"{action}_{channel_id}"
        return self.state.get(key)

    def clear_progress(self, action: str, channel_id: str):
        """
        Clear progress for a specific action and channel

        Args:
            action: Action type
            channel_id: Channel or guild ID
        """
        key = f"{action}_{channel_id}"
        if key in self.state:
            del self.state[key]
            self.save_state()

    def clear_all(self):
        """Clear all state"""
        self.state = {}
        self.save_state()


class ResumableDiscordScraper:
    """Discord scraper with resume capability"""

    def __init__(self, scraper, state_manager: Optional[StateManager] = None):
        """
        Initialize resumable scraper

        Args:
            scraper: DiscordScraper instance
            state_manager: StateManager instance (creates new if None)
        """
        self.scraper = scraper
        self.state_manager = state_manager or StateManager()

    def scrape_messages_resumable(
        self,
        channel_id: str,
        limit: Optional[int] = None,
        resume: bool = True
    ):
        """
        Scrape messages with resume capability

        Args:
            channel_id: Discord channel ID
            limit: Maximum number of messages to scrape
            resume: Whether to resume from previous state

        Returns:
            List of messages
        """
        all_messages = []
        before_id = None

        # Check for existing progress
        if resume:
            progress = self.state_manager.get_progress("scrapeMessages", channel_id)
            if progress:
                print(f"Resuming from previous state: {progress['scraped_count']} messages already scraped")
                before_id = progress['last_id']

        # Scrape messages with periodic state saving
        messages = self.scraper.scrape_messages(
            channel_id=channel_id,
            limit=limit,
            before=before_id
        )

        all_messages.extend(messages)

        # Update state after completion
        if messages:
            self.state_manager.update_progress(
                action="scrapeMessages",
                channel_id=channel_id,
                scraped_count=len(all_messages),
                last_id=messages[-1]["id"] if messages else None
            )

        return all_messages

    def scrape_members_resumable(
        self,
        guild_id: str,
        limit: Optional[int] = None,
        resume: bool = True
    ):
        """
        Scrape guild members with resume capability

        Args:
            guild_id: Discord guild ID
            limit: Maximum number of members to scrape
            resume: Whether to resume from previous state

        Returns:
            List of members
        """
        all_members = []

        # Check for existing progress
        if resume:
            progress = self.state_manager.get_progress("scrapeChannelMembers", guild_id)
            if progress:
                print(f"Resuming from previous state: {progress['scraped_count']} members already scraped")

        # Scrape members
        members = self.scraper.scrape_guild_members(
            guild_id=guild_id,
            limit=limit
        )

        all_members.extend(members)

        # Update state after completion
        if members:
            self.state_manager.update_progress(
                action="scrapeChannelMembers",
                channel_id=guild_id,
                scraped_count=len(all_members),
                last_id=members[-1]["user"]["id"] if members else None
            )

        return all_members
