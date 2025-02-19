import os
import pandas as pd
import discord
from discord.ext import commands
from dotenv import load_dotenv

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
        channel = discord.utils.get(guild.text_channels, name="general")  # Replace with channel name
        if channel:
            # Send initial message to channel
            await channel.send("$left")
            
            # Set up message storage
            messages = []
            
            # Read and save messages from channel
            async for message in channel.history(limit=1000):
                messages.append({
                    'author': message.author.name,
                    'content': message.content,
                    'timestamp': message.created_at
                })
                        # Save messages to CSV
            df = pd.DataFrame(messages)
            df.to_csv('discord_messages.csv', index=False)
            print(f"Saved {len(messages)} messages to discord_messages.csv")


# Run the client
client.run(TOKEN)