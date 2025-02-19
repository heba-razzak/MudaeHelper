"""
Discord Bot for Fetching Message History and Saving to CSV

How it Works:
1. The bot connects to Discord and searches for `general` channel.
2. It fetches the last `msg_limit` messages.
3. Captures both regular messages and embedded content (titles, descriptions, footers).
   - **Does NOT navigate through multiple embed pages**.
4. Saves messages as a CSV file in the `data` folder with the format:
   `hist<msg_limit>msgs_<timestamp>.csv`
   - Example: `hist10msgs_20250219_05-19-16.csv` (for the last 10 messages)
   - Example: `histAllmsgs_20250219_05-19-16.csv` (if fetching all messages)

Usage:
- Ensure the bot has `Read Message History` permissions.
- Change `msg_limit` if you want more or fewer messages.
- Modify `channel = discord.utils.get(guild.text_channels, name="general")` to fetch from a different channel.

Output:
- CSV file: `data/msg_history.csv`
- Example format:
    | author | content | timestamp |
    |--------|---------|-----------|
    | Mudae  | Page 1  | 2025-02-19 04:23:42 |
    | User1  | Hello!  | 2025-02-19 04:23:45 |
"""

import os
import pandas as pd
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Number of messages to save (Use `msg_limit = None` for full history)
msg_limit = 10

# Set up discord client with intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# get token from env
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        channel = discord.utils.get(guild.text_channels, name="general")  # Changed to mudae channel
        if channel:
            # Set up message storage
            messages = []
            
            # Read and save messages from channel
            async for message in channel.history(limit=msg_limit):
                msg_content = message.content
                if message.embeds:
                    for embed in message.embeds:
                        if embed.author.name:
                            msg_content = "\n".join([msg_content, embed.author.name])
                        if embed.description:
                            msg_content = "\n".join([msg_content, embed.description])
                        if embed.footer.text:
                            msg_content = "\n".join([msg_content, embed.footer.text])

                if msg_content:  # Only append if there is content
                    messages.append({
                        'author': message.author.name,
                        'content': msg_content,
                        'timestamp': message.created_at
                    })
            
            latest_timestamp = messages[0]["timestamp"].strftime("%Y%m%d_%H:%M:%S")  # Most recent message timestamp
            limit_str = str(msg_limit) if msg_limit is not None else "All"  # Use "All" for full history
            filename = f"data/hist{limit_str}msgs_{latest_timestamp}.csv"

            # Save messages to CSV
            df = pd.DataFrame(messages)
            df.to_csv(filename, index=False, encoding="utf-8")
            print(f"Saved {len(messages)} messages to msg_history.csv")

    await client.close()  # Quit the bot once messages are fetched

# Run the client
client.run(TOKEN)