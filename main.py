#!/usr/bin/env python3
"""
Discord Data Scraper - Main Entry Point
Similar to Apify's curious_coder/discord-data-scraper

Usage:
    python main.py --config config.json --token YOUR_TOKEN
    python main.py --action scrapeMessages --channel-url URL --token YOUR_TOKEN
"""

import argparse
import json
import sys
from datetime import datetime
from colorama import init, Fore, Style

from discord_scraper import DiscordScraper
from config_schema import ConfigSchema
from state_manager import StateManager, ResumableDiscordScraper

# Initialize colorama
init(autoreset=True)


def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════╗
║                                                       ║
║        Discord Data Scraper v1.0                     ║
║        Similar to Apify Discord Scraper              ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def get_discord_token():
    """
    Display instructions for getting Discord token
    """
    instructions = f"""
{Fore.YELLOW}═══════════════════════════════════════════════════════
How to Get Your Discord Token:
═══════════════════════════════════════════════════════{Style.RESET_ALL}

1. Open Discord in Google Chrome (or any browser)
2. Login to your Discord account
3. Press F12 to open Developer Tools
4. Go to the 'Console' tab
5. Paste this code and press Enter:

   {Fore.GREEN}(webpackChunkdiscord_app.push([[''],{{}},e=>{{m=[];for(let c in e.c)m.push(e.c[c])}}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken(){Style.RESET_ALL}

6. Copy the token that appears (without quotes)
7. Use it with --token parameter or save in config.json

{Fore.RED}⚠️  WARNING: Never share your token with anyone!
Keep it secret and secure.{Style.RESET_ALL}

{Fore.YELLOW}═══════════════════════════════════════════════════════{Style.RESET_ALL}
"""
    return instructions


def run_scraper(config: dict, token: str, resume: bool = True):
    """
    Run the scraper based on configuration

    Args:
        config: Configuration dictionary
        token: Discord authentication token
        resume: Whether to resume from previous state
    """
    try:
        # Validate configuration
        ConfigSchema.validate_config(config)

        # Get action and parameters
        action = config["action"]
        min_delay = config.get("minDelay", 1.0)
        max_delay = config.get("maxDelay", 3.0)

        # Create scraper
        scraper = DiscordScraper(token=token, min_delay=min_delay, max_delay=max_delay)
        state_manager = StateManager()
        resumable_scraper = ResumableDiscordScraper(scraper, state_manager)

        # Execute action
        if action == "scrapeMessages":
            params = config["scrapeMessages"]
            channel_url = params["channelUrl"]
            guild_id, channel_id = DiscordScraper.parse_channel_url(channel_url)

            print(f"{Fore.CYAN}Action: Scrape Messages")
            print(f"{Fore.CYAN}Channel URL: {channel_url}")
            print(f"{Fore.CYAN}Guild ID: {guild_id}")
            print(f"{Fore.CYAN}Channel ID: {channel_id}")
            print()

            # Get channel info
            channel_info = scraper.get_channel_info(channel_id)
            if channel_info:
                print(f"{Fore.GREEN}✓ Channel: {channel_info.get('name', 'Unknown')}")
                print()

            # Scrape messages
            messages = resumable_scraper.scrape_messages_resumable(
                channel_id=channel_id,
                limit=params.get("limit"),
                resume=resume
            )

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"messages_{channel_id}_{timestamp}.json"
            scraper.save_to_json(messages, filename)

            # Display summary
            print()
            print(f"{Fore.GREEN}╔═══════════════════════════════════════════════════════╗")
            print(f"{Fore.GREEN}║  Scraping Complete!                                   ║")
            print(f"{Fore.GREEN}╚═══════════════════════════════════════════════════════╝")
            print(f"{Fore.CYAN}Total messages scraped: {len(messages)}")
            print(f"{Fore.CYAN}Output file: output/{filename}")

            # Clear state on successful completion
            state_manager.clear_progress("scrapeMessages", channel_id)

        elif action == "scrapeChannelMembers":
            params = config["scrapeChannelMembers"]
            channel_url = params["channelUrl"]
            guild_id, channel_id = DiscordScraper.parse_channel_url(channel_url)

            print(f"{Fore.CYAN}Action: Scrape Guild Members")
            print(f"{Fore.CYAN}Channel URL: {channel_url}")
            print(f"{Fore.CYAN}Guild ID: {guild_id}")
            print()

            # Get guild info
            guild_info = scraper.get_guild_info(guild_id)
            if guild_info:
                print(f"{Fore.GREEN}✓ Guild: {guild_info.get('name', 'Unknown')}")
                print()

            # Scrape members
            members = resumable_scraper.scrape_members_resumable(
                guild_id=guild_id,
                limit=params.get("limit"),
                resume=resume
            )

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"members_{guild_id}_{timestamp}.json"
            scraper.save_to_json(members, filename)

            # Display summary
            print()
            print(f"{Fore.GREEN}╔═══════════════════════════════════════════════════════╗")
            print(f"{Fore.GREEN}║  Scraping Complete!                                   ║")
            print(f"{Fore.GREEN}╚═══════════════════════════════════════════════════════╝")
            print(f"{Fore.CYAN}Total members scraped: {len(members)}")
            print(f"{Fore.CYAN}Output file: output/{filename}")

            # Clear state on successful completion
            state_manager.clear_progress("scrapeChannelMembers", guild_id)

    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Discord Data Scraper - Scrape messages and members from Discord",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using config file
  python main.py --config config.json --token YOUR_TOKEN

  # Scrape messages from channel
  python main.py --action scrapeMessages --channel-url "https://discord.com/channels/123/456" --token YOUR_TOKEN

  # Scrape members from guild
  python main.py --action scrapeChannelMembers --channel-url "https://discord.com/channels/123/456" --token YOUR_TOKEN

  # Get help on obtaining Discord token
  python main.py --get-token

  # Generate example config
  python main.py --example-config
        """
    )

    parser.add_argument("--config", help="Path to JSON configuration file")
    parser.add_argument("--token", help="Discord authentication token")
    parser.add_argument("--action", choices=["scrapeMessages", "scrapeChannelMembers"],
                        help="Action to perform")
    parser.add_argument("--channel-url", help="Discord channel URL")
    parser.add_argument("--limit", type=int, help="Maximum number of items to scrape")
    parser.add_argument("--min-delay", type=float, default=1.0,
                        help="Minimum delay between requests (default: 1.0)")
    parser.add_argument("--max-delay", type=float, default=3.0,
                        help="Maximum delay between requests (default: 3.0)")
    parser.add_argument("--no-resume", action="store_true",
                        help="Don't resume from previous state")
    parser.add_argument("--get-token", action="store_true",
                        help="Show instructions for getting Discord token")
    parser.add_argument("--example-config", action="store_true",
                        help="Generate example configuration files")

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Handle special arguments
    if args.get_token:
        print(get_discord_token())
        sys.exit(0)

    if args.example_config:
        print(f"{Fore.CYAN}Generating example configuration files...")

        # Example for scraping messages
        msg_config = ConfigSchema.create_scrape_messages_config(
            channel_url="https://discord.com/channels/YOUR_GUILD_ID/YOUR_CHANNEL_ID",
            min_delay=1.0,
            max_delay=3.0,
            limit=1000
        )
        with open("config_scrape_messages.json", 'w') as f:
            json.dump(msg_config, f, indent=2)
        print(f"{Fore.GREEN}✓ Created: config_scrape_messages.json")

        # Example for scraping members
        member_config = ConfigSchema.create_scrape_members_config(
            channel_url="https://discord.com/channels/YOUR_GUILD_ID/YOUR_CHANNEL_ID",
            min_delay=1.0,
            max_delay=3.0,
            limit=1000
        )
        with open("config_scrape_members.json", 'w') as f:
            json.dump(member_config, f, indent=2)
        print(f"{Fore.GREEN}✓ Created: config_scrape_members.json")

        print(f"\n{Fore.CYAN}Edit these files and run with:")
        print(f"{Fore.YELLOW}python main.py --config config_scrape_messages.json --token YOUR_TOKEN")
        sys.exit(0)

    # Validate token
    if not args.token:
        print(f"{Fore.RED}Error: Discord token is required!")
        print(f"{Fore.YELLOW}Use --get-token to see how to obtain your token")
        sys.exit(1)

    # Build configuration
    if args.config:
        # Load from config file
        print(f"{Fore.CYAN}Loading configuration from {args.config}...")
        config = ConfigSchema.load_from_file(args.config)
    elif args.action and args.channel_url:
        # Build from command line arguments
        if args.action == "scrapeMessages":
            config = ConfigSchema.create_scrape_messages_config(
                channel_url=args.channel_url,
                min_delay=args.min_delay,
                max_delay=args.max_delay,
                limit=args.limit
            )
        else:  # scrapeChannelMembers
            config = ConfigSchema.create_scrape_members_config(
                channel_url=args.channel_url,
                min_delay=args.min_delay,
                max_delay=args.max_delay,
                limit=args.limit
            )
    else:
        print(f"{Fore.RED}Error: Either --config or (--action and --channel-url) are required!")
        parser.print_help()
        sys.exit(1)

    # Run scraper
    run_scraper(config, args.token, resume=not args.no_resume)


if __name__ == "__main__":
    main()
