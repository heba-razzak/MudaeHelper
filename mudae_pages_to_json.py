"""
Discord Bot for Capturing Mudae Command Pages

How it Works:
1. Send a Mudae command in Discord (e.g., `$top`, `$top k 100`).
2. The bot will detect the command and start tracking pages.
3. Flip through the pages manually to let the bot capture them sequentially.
4. The bot ensures pages are saved in order and waits if a page is skipped.
5. Once all pages are captured, the file is saved in the `data` folder.

Output:
- JSON file named as `<command>_<timestamp>.json`
- Example: `top_20250219_05:03:31.json`

Make sure:
- The bot has permissions to read messages in the channel.
- You manually flip the pages to allow full data capture.
"""

import os
import json
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
import re

# Load the bot token
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up discord client with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Store captured pages
captured_pages = []
expected_page_number = 1  # Start at Page 1
current_command = None  # Store the command that triggered the capture
save_filename = None  # Dynamic filename
waiting_flag = False # Ensures "Waiting for Page X" is printed only once per missing page

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    # Find the first available channel with Mudae messages
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).read_messages:
                print(f"Listening for Mudae messages in: {channel.name} ({guild.name})")
                bot.loop.create_task(track_mudae_pages(channel))  # Start tracking pages
                return  # Only track one channel

@bot.event
async def on_message(message):
    global current_command, save_filename, expected_page_number, captured_pages

    if message.author.bot:
        return  # Ignore bot messages

    # Detect if the user sent a Mudae command (e.g., "$top", "$topk")
    if message.content.startswith("$"):
        current_command = message.content.strip().replace(" ", "_")  # Store command, Replace spaces with _

        # Convert message timestamp to the desired format
        timestamp = message.created_at.strftime("%Y%m%d_%H:%M:%S")  # Extracts up to seconds

        # Set the filename (removing "$" from the command name)
        save_filename = f"{current_command[1:]}_{timestamp}.json"

        # Reset tracking variables
        expected_page_number = 1  
        captured_pages = []  
        waiting_flag = False  # Reset waiting flag

        print(f"🔍 Tracking new command: {current_command}, saving to {save_filename}")

async def track_mudae_pages(channel):
    """ Continuously check for new Mudae pages every second. """
    global expected_page_number, save_filename, waiting_flag, expected_page_number, captured_pages

    while True:
        await asyncio.sleep(1)  # Wait 1 second before checking again

        # Fetch the latest message in the channel
        async for message in channel.history(limit=1):
            if message.author.name == "Mudae" and message.embeds:
                embed = message.embeds[0]  # Get the first embed
                
                # Extract page number using regex (e.g., "Page 2 / 67" → 2)
                match = re.search(r"(\d+) / (\d+)", embed.footer.text if embed.footer else "")
                # match = re.search(r"Page (\d+) / (\d+)", embed.footer.text if embed.footer else "")
                if match:
                    current_page = int(match.group(1))
                    total_pages = int(match.group(2))
                    
                    # Only save if we are on the expected page
                    if current_page == expected_page_number:
                        embed_data = {
                            'page': embed.footer.text,
                            'description': embed.description if embed.description else "No description",
                            'timestamp': str(message.created_at),
                            'channel': message.channel.name,
                            'guild': message.guild.name
                        }
                        captured_pages.append(embed_data)

                        # Save to dynamically named JSON file
                        if save_filename:
                            with open(os.path.join("data", save_filename), "w", encoding="utf-8") as file:
                                json.dump(captured_pages, file, indent=4, ensure_ascii=False)

                        print(f"✅ Captured and saved: {embed.footer.text} -> {save_filename}")
                        expected_page_number += 1  # Move to the next page
                        waiting_flag = False
                    elif current_page > expected_page_number and not waiting_flag:
                        print(f"⏳ Waiting for Page {expected_page_number}")
                        waiting_flag = True

bot.run(TOKEN)