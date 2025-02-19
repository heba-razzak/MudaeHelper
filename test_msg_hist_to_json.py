import os
import json
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands

# Load the bot token
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up discord client with intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Helper function to handle pagination of embeds
async def get_all_embed_pages(message, embed):
    # Check if embed has pagination (footer with "Page X / Y" format)
    if not (embed.footer and embed.footer.text and " / " in embed.footer.text):
        return [embed.to_dict()]
        
    # Extract total pages from footer
    try:
        current_page, total_pages = map(int, embed.footer.text.split(" / "))
    except:
        return [embed.to_dict()]
        
    all_embeds = [embed.to_dict()]
    
    # Get subsequent pages by simulating pagination reactions
    for page in range(2, total_pages + 1):
        # Wait briefly to avoid rate limiting
        await asyncio.sleep(1)
        
        # Add right arrow reaction to move to next page
        try:
            await message.add_reaction("➡️")
            # Wait for embed to update
            await asyncio.sleep(1)
            # Get updated message
            updated_message = await message.channel.fetch_message(message.id)
            if updated_message.embeds:
                all_embeds.append(updated_message.embeds[0].to_dict())
        except:
            break
            
        # Remove reaction to clean up
        await message.remove_reaction("➡️", client.user)
            
    return all_embeds

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).read_messages:
                print(f"Fetching messages from {channel.name} in {guild.name}")
                
                messages = []
                async for message in channel.history(limit=None):
                    msg_data = {
                        'author': message.author.name,
                        'content': message.content,
                        'timestamp': str(message.created_at),
                        'embeds': [],
                        # 'embeds': [embed.to_dict() for embed in message.embeds],
                        'attachments': [att.url for att in message.attachments],
                        'id': message.id,
                        'channel': message.channel.name,
                        'guild': message.guild.name
                    }
                    
                    # Handle embeds with pagination
                    for embed in message.embeds:
                        embed_pages = await get_all_embed_pages(message, embed)
                        msg_data['embeds'].extend(embed_pages)
                    
                    messages.append(msg_data)

                # Save messages to JSON
                with open('data/msg_history.json', 'w', encoding='utf-8') as file:
                    json.dump(messages, file, ensure_ascii=False, indent=4)

                print(f"Saved {len(messages)} messages to msg_history.json")
                break  # Only process one channel

    await client.close()  # Shut down the bot after fetching messages

# Run the bot
client.run(TOKEN)