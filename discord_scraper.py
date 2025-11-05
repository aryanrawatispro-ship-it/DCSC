"""
Discord Data Scraper
Scrapes messages and members from Discord channels using Discord API
"""

import requests
import json
import time
import random
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)


class DiscordScraper:
    """Main Discord scraper class for scraping messages and members"""

    BASE_URL = "https://discord.com/api/v9"

    def __init__(self, token: str, min_delay: float = 1.0, max_delay: float = 3.0):
        """
        Initialize Discord scraper

        Args:
            token: Discord authentication token
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
        """
        self.token = token
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _delay(self):
        """Random delay between requests to avoid rate limiting"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """
        Make HTTP request to Discord API with error handling

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON or None if failed
        """
        try:
            response = self.session.request(method, url, **kwargs)

            if response.status_code == 429:
                # Rate limited
                retry_after = response.json().get('retry_after', 5)
                print(f"{Fore.YELLOW}Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self._make_request(method, url, **kwargs)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 204:
                return {}
            else:
                print(f"{Fore.RED}Request failed with status {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"{Fore.RED}Request error: {str(e)}")
            return None

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """
        Get information about a Discord channel

        Args:
            channel_id: Discord channel ID

        Returns:
            Channel information dict or None
        """
        url = f"{self.BASE_URL}/channels/{channel_id}"
        return self._make_request("GET", url)

    def get_guild_info(self, guild_id: str) -> Optional[Dict]:
        """
        Get information about a Discord guild/server

        Args:
            guild_id: Discord guild ID

        Returns:
            Guild information dict or None
        """
        url = f"{self.BASE_URL}/guilds/{guild_id}"
        return self._make_request("GET", url)

    def scrape_messages(
        self,
        channel_id: str,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape messages from a Discord channel

        Args:
            channel_id: Discord channel ID
            limit: Maximum number of messages to scrape (None for all)
            before: Get messages before this message ID
            after: Get messages after this message ID

        Returns:
            List of message dictionaries
        """
        all_messages = []
        last_message_id = before
        total_scraped = 0

        print(f"{Fore.GREEN}Starting message scraping for channel {channel_id}...")

        while True:
            # Build query parameters
            params = {"limit": 100}
            if last_message_id:
                params["before"] = last_message_id
            if after:
                params["after"] = after

            # Make request
            url = f"{self.BASE_URL}/channels/{channel_id}/messages"
            messages = self._make_request("GET", url, params=params)

            if not messages or len(messages) == 0:
                print(f"{Fore.CYAN}No more messages to scrape")
                break

            # Process messages
            for msg in messages:
                processed_msg = self._process_message(msg)
                all_messages.append(processed_msg)
                total_scraped += 1

                if limit and total_scraped >= limit:
                    print(f"{Fore.GREEN}Reached limit of {limit} messages")
                    return all_messages

            last_message_id = messages[-1]["id"]
            print(f"{Fore.CYAN}Scraped {total_scraped} messages so far...")

            # Delay before next request
            self._delay()

        print(f"{Fore.GREEN}✓ Scraped total of {total_scraped} messages")
        return all_messages

    def _process_message(self, msg: Dict) -> Dict[str, Any]:
        """
        Process and format a Discord message

        Args:
            msg: Raw message dict from Discord API

        Returns:
            Processed message dict
        """
        return {
            "id": msg.get("id"),
            "channel_id": msg.get("channel_id"),
            "author": {
                "id": msg.get("author", {}).get("id"),
                "username": msg.get("author", {}).get("username"),
                "discriminator": msg.get("author", {}).get("discriminator"),
                "avatar": msg.get("author", {}).get("avatar"),
                "bot": msg.get("author", {}).get("bot", False)
            },
            "content": msg.get("content"),
            "timestamp": msg.get("timestamp"),
            "edited_timestamp": msg.get("edited_timestamp"),
            "tts": msg.get("tts", False),
            "mention_everyone": msg.get("mention_everyone", False),
            "mentions": [
                {
                    "id": m.get("id"),
                    "username": m.get("username"),
                    "discriminator": m.get("discriminator")
                }
                for m in msg.get("mentions", [])
            ],
            "attachments": [
                {
                    "id": a.get("id"),
                    "filename": a.get("filename"),
                    "size": a.get("size"),
                    "url": a.get("url"),
                    "proxy_url": a.get("proxy_url"),
                    "width": a.get("width"),
                    "height": a.get("height"),
                    "content_type": a.get("content_type")
                }
                for a in msg.get("attachments", [])
            ],
            "embeds": msg.get("embeds", []),
            "reactions": msg.get("reactions", []),
            "pinned": msg.get("pinned", False),
            "type": msg.get("type")
        }

    def scrape_guild_members(
        self,
        guild_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape members from a Discord guild/server

        Args:
            guild_id: Discord guild ID
            limit: Maximum number of members to scrape (None for all)

        Returns:
            List of member dictionaries
        """
        all_members = []
        after_id = "0"
        total_scraped = 0

        print(f"{Fore.GREEN}Starting member scraping for guild {guild_id}...")

        while True:
            # Build query parameters
            params = {"limit": 1000, "after": after_id}

            # Make request
            url = f"{self.BASE_URL}/guilds/{guild_id}/members"
            members = self._make_request("GET", url, params=params)

            if not members or len(members) == 0:
                print(f"{Fore.CYAN}No more members to scrape")
                break

            # Process members
            for member in members:
                processed_member = self._process_member(member)
                all_members.append(processed_member)
                total_scraped += 1

                if limit and total_scraped >= limit:
                    print(f"{Fore.GREEN}Reached limit of {limit} members")
                    return all_members

            # Get last member ID for pagination
            after_id = members[-1]["user"]["id"]
            print(f"{Fore.CYAN}Scraped {total_scraped} members so far...")

            # Delay before next request
            self._delay()

        print(f"{Fore.GREEN}✓ Scraped total of {total_scraped} members")
        return all_members

    def _process_member(self, member: Dict) -> Dict[str, Any]:
        """
        Process and format a Discord member

        Args:
            member: Raw member dict from Discord API

        Returns:
            Processed member dict
        """
        user = member.get("user", {})
        return {
            "user": {
                "id": user.get("id"),
                "username": user.get("username"),
                "discriminator": user.get("discriminator"),
                "avatar": user.get("avatar"),
                "bot": user.get("bot", False),
                "system": user.get("system", False),
                "public_flags": user.get("public_flags")
            },
            "nick": member.get("nick"),
            "roles": member.get("roles", []),
            "joined_at": member.get("joined_at"),
            "premium_since": member.get("premium_since"),
            "deaf": member.get("deaf", False),
            "mute": member.get("mute", False),
            "pending": member.get("pending", False),
            "permissions": member.get("permissions")
        }

    @staticmethod
    def parse_channel_url(url: str) -> tuple:
        """
        Parse Discord channel URL to extract guild and channel IDs

        Args:
            url: Discord channel URL (e.g., https://discord.com/channels/123/456)

        Returns:
            Tuple of (guild_id, channel_id)
        """
        parts = url.rstrip('/').split('/')
        if len(parts) >= 2:
            channel_id = parts[-1]
            guild_id = parts[-2]
            return guild_id, channel_id
        raise ValueError("Invalid Discord channel URL")

    def save_to_json(self, data: List[Dict], filename: str):
        """
        Save data to JSON file

        Args:
            data: Data to save
            filename: Output filename
        """
        os.makedirs("output", exist_ok=True)
        filepath = os.path.join("output", filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"{Fore.GREEN}✓ Saved {len(data)} records to {filepath}")
