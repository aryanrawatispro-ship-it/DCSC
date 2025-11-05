# Discord Data Scraper (DCSC)

A powerful Discord data scraper similar to [Apify's curious_coder/discord-data-scraper](https://apify.com/curious_coder/discord-data-scraper). Scrape messages and members from Discord channels and servers with ease.

## Features

✨ **Scrape Messages** - Extract messages from any Discord channel with attachments, embeds, and reactions

👥 **Scrape Members** - Get all members from a Discord server/guild with roles and permissions

⏸️ **Resume Capability** - Automatically resume scraping if interrupted

🔄 **Rate Limit Handling** - Smart delays and automatic retry on rate limits

📊 **Structured Output** - Clean JSON output format similar to Apify

🎨 **Beautiful CLI** - Colorful terminal interface with progress tracking

🌐 **Web Interface** - Beautiful web GUI similar to Apify with real-time progress tracking

## Web Interface (NEW!)

The Discord Data Scraper now includes a **beautiful web-based GUI** similar to Apify's interface!

### Features
- 🎨 Modern, responsive web interface
- ⚙️ Easy configuration with forms
- ⏱️ Real-time progress tracking with Socket.IO
- 📊 Live log output
- 💾 Download results as JSON
- 👁️ Preview results in browser
- 🔧 Full customization options:
  - Token input
  - No timeout option
  - Configurable delays
  - Message limits
  - Before/After message ID filters

### Quick Start (Web Interface)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the web server:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

4. Fill in the form:
   - Enter your Discord token (click "How to get your Discord token?" for help)
   - Select action (Scrape Messages or Scrape Members)
   - Enter channel URL
   - Configure advanced options if needed
   - Click "Start Scraping"

5. Watch real-time progress and download results!

### Web Interface Screenshots

The web interface includes:
- **Configuration Form** - Easy input with validation
- **Advanced Options** - Collapsible section for fine-tuning
- **Real-time Progress** - Live updates with Socket.IO
- **Log Output** - See what's happening in real-time
- **Results Viewer** - Preview and download your data
- **Recent Jobs** - Quick access to previous scrapes

## VPS Deployment

**Want to deploy on your Ubuntu VPS?** We've got you covered!

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete VPS deployment instructions including:
- Automated installation script
- Systemd service setup
- Nginx reverse proxy configuration
- SSL/HTTPS setup with Let's Encrypt
- Security best practices

**Quick VPS Install:**
```bash
cd DCSC/deployment
chmod +x install_vps.sh
./install_vps.sh
```

## Installation

### Prerequisites

- Python 3.7 or higher
- A Discord account
- Discord authentication token (see [Getting Your Discord Token](#getting-your-discord-token))

### Setup

1. Clone or download this repository:
```bash
git clone <repository-url>
cd DCSC
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Getting Your Discord Token

⚠️ **WARNING**: Your Discord token is sensitive! Never share it with anyone.

1. Open Discord in Google Chrome (or any browser)
2. Login to your Discord account
3. Press `F12` to open Developer Tools
4. Go to the **Console** tab
5. Paste this code and press Enter:

```javascript
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
```

6. Copy the token that appears (without quotes)
7. Use it with the `--token` parameter

**Alternative method:** You can also run:
```bash
python main.py --get-token
```

## Usage

You can use the Discord Data Scraper in two ways:
1. **Web Interface** (Recommended) - Beautiful GUI similar to Apify
2. **Command Line** - Terminal-based interface for automation

### Quick Start (Command Line)

#### Scrape Messages from a Channel

```bash
python main.py \
  --action scrapeMessages \
  --channel-url "https://discord.com/channels/123456789/987654321" \
  --token "YOUR_DISCORD_TOKEN"
```

#### Scrape Members from a Server

```bash
python main.py \
  --action scrapeChannelMembers \
  --channel-url "https://discord.com/channels/123456789/987654321" \
  --token "YOUR_DISCORD_TOKEN"
```

### Using Configuration Files

For more control, use JSON configuration files similar to Apify's input schema.

#### Generate Example Configs

```bash
python main.py --example-config
```

This creates:
- `config_scrape_messages.json` - Example for scraping messages
- `config_scrape_members.json` - Example for scraping members

#### Run with Config File

```bash
python main.py --config config_scrape_messages.json --token "YOUR_DISCORD_TOKEN"
```

### Configuration Schema

#### Scrape Messages Config

```json
{
  "action": "scrapeMessages",
  "scrapeMessages": {
    "channelUrl": "https://discord.com/channels/GUILD_ID/CHANNEL_ID",
    "limit": 1000,
    "before": null,
    "after": null
  },
  "minDelay": 1,
  "maxDelay": 3
}
```

**Parameters:**
- `channelUrl` (required): Discord channel URL
- `limit` (optional): Maximum number of messages to scrape (null = all)
- `before` (optional): Scrape messages before this message ID
- `after` (optional): Scrape messages after this message ID
- `minDelay`: Minimum delay between requests in seconds (default: 1)
- `maxDelay`: Maximum delay between requests in seconds (default: 3)

#### Scrape Members Config

```json
{
  "action": "scrapeChannelMembers",
  "scrapeChannelMembers": {
    "channelUrl": "https://discord.com/channels/GUILD_ID/CHANNEL_ID",
    "limit": null
  },
  "minDelay": 1,
  "maxDelay": 3
}
```

**Parameters:**
- `channelUrl` (required): Discord channel URL (guild ID will be extracted)
- `limit` (optional): Maximum number of members to scrape (null = all)
- `minDelay`: Minimum delay between requests in seconds (default: 1)
- `maxDelay`: Maximum delay between requests in seconds (default: 3)

### Command Line Options

```
Options:
  --config CONFIG           Path to JSON configuration file
  --token TOKEN            Discord authentication token
  --action {scrapeMessages,scrapeChannelMembers}
                           Action to perform
  --channel-url URL        Discord channel URL
  --limit LIMIT            Maximum number of items to scrape
  --min-delay SECONDS      Minimum delay between requests (default: 1.0)
  --max-delay SECONDS      Maximum delay between requests (default: 3.0)
  --no-resume              Don't resume from previous state
  --get-token              Show instructions for getting Discord token
  --example-config         Generate example configuration files
  -h, --help               Show help message
```

## Output Format

### Messages Output

Scraped messages are saved as JSON with the following structure:

```json
[
  {
    "id": "123456789012345678",
    "channel_id": "987654321098765432",
    "author": {
      "id": "111222333444555666",
      "username": "username",
      "discriminator": "1234",
      "avatar": "avatar_hash",
      "bot": false
    },
    "content": "Message content here",
    "timestamp": "2024-01-01T12:00:00.000000+00:00",
    "edited_timestamp": null,
    "attachments": [
      {
        "id": "attachment_id",
        "filename": "image.png",
        "size": 123456,
        "url": "https://cdn.discordapp.com/...",
        "proxy_url": "https://media.discordapp.net/...",
        "width": 1920,
        "height": 1080,
        "content_type": "image/png"
      }
    ],
    "embeds": [],
    "reactions": [],
    "mentions": [],
    "pinned": false,
    "type": 0
  }
]
```

### Members Output

Scraped members are saved as JSON with the following structure:

```json
[
  {
    "user": {
      "id": "123456789012345678",
      "username": "username",
      "discriminator": "1234",
      "avatar": "avatar_hash",
      "bot": false,
      "system": false,
      "public_flags": 0
    },
    "nick": "Server Nickname",
    "roles": ["role_id_1", "role_id_2"],
    "joined_at": "2023-01-01T00:00:00.000000+00:00",
    "premium_since": null,
    "deaf": false,
    "mute": false,
    "pending": false,
    "permissions": "1234567890"
  }
]
```

## Features Comparison with Apify Scraper

| Feature | DCSC | Apify curious_coder |
|---------|------|---------------------|
| Scrape Messages | ✅ | ✅ |
| Scrape Members | ✅ | ✅ |
| Attachments | ✅ | ✅ |
| Rate Limit Handling | ✅ | ✅ |
| Resume Capability | ✅ | ✅ |
| Configurable Delays | ✅ | ✅ |
| JSON Output | ✅ | ✅ |
| Web Interface | ✅ | ✅ |
| Real-time Progress | ✅ | ✅ |
| CLI Interface | ✅ | ❌ |
| No Timeout Option | ✅ | ❓ |
| Free to Use | ✅ | ❌ ($19/month) |
| Open Source | ✅ | ❌ |
| Local Execution | ✅ | ❌ |

## Examples

### Example 1: Scrape Last 500 Messages

```bash
python main.py \
  --action scrapeMessages \
  --channel-url "https://discord.com/channels/123/456" \
  --limit 500 \
  --token "YOUR_TOKEN"
```

### Example 2: Scrape All Members with Slow Rate

```bash
python main.py \
  --action scrapeChannelMembers \
  --channel-url "https://discord.com/channels/123/456" \
  --min-delay 2 \
  --max-delay 5 \
  --token "YOUR_TOKEN"
```

### Example 3: Resume Interrupted Scraping

If scraping is interrupted, simply run the same command again. The scraper will automatically resume from where it left off:

```bash
# Run this command
python main.py --config config.json --token "YOUR_TOKEN"

# If interrupted, run the same command again - it will resume!
python main.py --config config.json --token "YOUR_TOKEN"
```

### Example 4: Fresh Start (No Resume)

```bash
python main.py \
  --config config.json \
  --token "YOUR_TOKEN" \
  --no-resume
```

## Output Files

All output files are saved in the `output/` directory with timestamped filenames:

- Messages: `output/messages_{CHANNEL_ID}_{TIMESTAMP}.json`
- Members: `output/members_{GUILD_ID}_{TIMESTAMP}.json`

State file for resume capability: `state.json`

## API as Python Module

You can also use the scraper as a Python module in your own scripts:

```python
from discord_scraper import DiscordScraper

# Create scraper instance
scraper = DiscordScraper(token="YOUR_TOKEN", min_delay=1, max_delay=3)

# Scrape messages
messages = scraper.scrape_messages(channel_id="123456789")

# Scrape members
members = scraper.scrape_guild_members(guild_id="987654321")

# Save to JSON
scraper.save_to_json(messages, "my_messages.json")
```

## Rate Limiting

The scraper includes smart rate limit handling:

- Random delays between requests (configurable via `minDelay` and `maxDelay`)
- Automatic retry with backoff when rate limited
- Discord API respects rate limit headers

**Recommendations:**
- Use `minDelay=1` and `maxDelay=3` for normal scraping
- Use `minDelay=2` and `maxDelay=5` for large servers to avoid rate limits
- The scraper will automatically wait if rate limited by Discord

## Troubleshooting

### Error: 401 Unauthorized
- Your Discord token is invalid or expired
- Get a new token using the instructions above

### Error: 403 Forbidden
- You don't have permission to access the channel/server
- Make sure you're a member of the server
- Check if the channel is private

### Error: 404 Not Found
- The channel URL is incorrect
- The channel may have been deleted

### Rate Limited
- The scraper automatically handles rate limits
- If you see frequent rate limits, increase `minDelay` and `maxDelay`

## Legal & Ethical Considerations

⚠️ **Important Disclaimers:**

1. **Terms of Service**: Scraping Discord may violate Discord's Terms of Service. Use at your own risk.

2. **Privacy**: Respect user privacy. Don't scrape or share private conversations without consent.

3. **Rate Limits**: Don't abuse Discord's API. Use appropriate delays.

4. **Purpose**: This tool is for educational purposes and legitimate use cases like:
   - Backing up your own server data
   - Research with proper authorization
   - Archiving public channels with permission

5. **Responsibility**: You are responsible for how you use this tool.

## License

This project is provided as-is for educational purposes. Use responsibly and ethically.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Comparison with Apify

This tool provides similar functionality to Apify's curious_coder/discord-data-scraper but:

- ✅ **Free** - No monthly subscription required
- ✅ **Open Source** - Full transparency and customization
- ✅ **Local** - Your data stays on your machine
- ✅ **CLI** - Easy command-line interface
- ✅ **Flexible** - Use as module or standalone tool

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ for the Discord community**
