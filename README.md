# Discord Casino Bot

This Discord bot provides a fun casino experience for your server, including games like blackjack, roulette, and slots.

## Features

- Multiple casino games: Blackjack, Roulette, Slots, Dice
- User balance tracking
- Leaderboards
- Magic 8-ball responses

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Discord account and a Discord server where you have permissions to add bots

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/discord-casino-bot.git
   cd discord-casino-bot
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

## Setting up the Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click "New Application" and give it a name.
3. Go to the "Bot" tab and click "Add Bot".
4. Under the bot's username, click "Copy" to copy the bot's token.
5. Paste this token in your `.env` file.

## Running the Bot

1. Run the main script:
   ```
   python main.py
   ```

2. The bot should now be online and ready to use in your Discord server.

## Usage

Use the following commands in your Discord server:

- `pls help`: Show all available commands
- `pls start`: Start your casino journey
- `pls gamble`: View gambling options
- `pls profile`: View your profile
- `pls leaderboard <stat>`: View leaderboards

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This bot is for entertainment purposes only. No real money is involved.
