"""
Configuration schema and validation for Discord scraper
"""

from typing import Dict, Any, Optional
import json


class ConfigSchema:
    """Input configuration schema similar to Apify format"""

    @staticmethod
    def create_scrape_messages_config(
        channel_url: str,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create configuration for scraping messages

        Args:
            channel_url: Discord channel URL
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
            limit: Maximum number of messages to scrape
            before: Get messages before this message ID
            after: Get messages after this message ID

        Returns:
            Configuration dictionary
        """
        return {
            "action": "scrapeMessages",
            "scrapeMessages": {
                "channelUrl": channel_url,
                "limit": limit,
                "before": before,
                "after": after
            },
            "minDelay": min_delay,
            "maxDelay": max_delay
        }

    @staticmethod
    def create_scrape_members_config(
        channel_url: str,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create configuration for scraping guild members

        Args:
            channel_url: Discord channel URL (guild will be extracted)
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
            limit: Maximum number of members to scrape

        Returns:
            Configuration dictionary
        """
        return {
            "action": "scrapeChannelMembers",
            "scrapeChannelMembers": {
                "channelUrl": channel_url,
                "limit": limit
            },
            "minDelay": min_delay,
            "maxDelay": max_delay
        }

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate configuration dictionary

        Args:
            config: Configuration to validate

        Returns:
            True if valid, raises ValueError if invalid
        """
        if "action" not in config:
            raise ValueError("Missing 'action' field in config")

        action = config["action"]
        if action not in ["scrapeMessages", "scrapeChannelMembers"]:
            raise ValueError(f"Invalid action: {action}")

        if action == "scrapeMessages":
            if "scrapeMessages" not in config:
                raise ValueError("Missing 'scrapeMessages' configuration")
            if "channelUrl" not in config["scrapeMessages"]:
                raise ValueError("Missing 'channelUrl' in scrapeMessages config")

        elif action == "scrapeChannelMembers":
            if "scrapeChannelMembers" not in config:
                raise ValueError("Missing 'scrapeChannelMembers' configuration")
            if "channelUrl" not in config["scrapeChannelMembers"]:
                raise ValueError("Missing 'channelUrl' in scrapeChannelMembers config")

        return True

    @staticmethod
    def load_from_file(filepath: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file

        Args:
            filepath: Path to JSON configuration file

        Returns:
            Configuration dictionary
        """
        with open(filepath, 'r') as f:
            config = json.load(f)

        ConfigSchema.validate_config(config)
        return config

    @staticmethod
    def save_to_file(config: Dict[str, Any], filepath: str):
        """
        Save configuration to JSON file

        Args:
            config: Configuration dictionary
            filepath: Path to save JSON file
        """
        ConfigSchema.validate_config(config)

        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)


# Example configurations
EXAMPLE_SCRAPE_MESSAGES = {
    "action": "scrapeMessages",
    "scrapeMessages": {
        "channelUrl": "https://discord.com/channels/GUILD_ID/CHANNEL_ID",
        "limit": None,
        "before": None,
        "after": None
    },
    "minDelay": 1,
    "maxDelay": 3
}

EXAMPLE_SCRAPE_MEMBERS = {
    "action": "scrapeChannelMembers",
    "scrapeChannelMembers": {
        "channelUrl": "https://discord.com/channels/GUILD_ID/CHANNEL_ID",
        "limit": None
    },
    "minDelay": 1,
    "maxDelay": 3
}
