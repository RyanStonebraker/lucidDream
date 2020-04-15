import os
import discord
import contextlib

from dotenv import load_dotenv

import generator
import pandas as pd

# characters = ["arsh", "bradley", "percy", "charlie", "neville", "fred", "george", "molly", "percival graves", "lucas", "flinch", "grindelwald", "dobby", "cedric", "myrtle", "harry", "ron", "hermione", "snape", "albus dumbledore", "dumbledore", "tom riddle", "hagrid", "environment", "voldemort", "malfoy", "draco", "mcgonagall", "lupin", "sirius", "hedwig", "headless nick", "dudley", "vernon", "arthur", "ginny", "crab", "goyle", "voldemort"]

# characters = ["arsh", "bradley", "nathan", "addeline", "tristan", "ryan", "george", "andrew", "matt", "ian", "izac", "jason", "tyler", "harry", "hermione", "ron", "tyler"]

characters = {
    "arsh": "Van Arsh",
    "bradley": "Bradley Morton",
    "nathan": "Nathan VanOverbeke",
    "addeline": "Addeline",
    "tristan": "Tristan Van Cise",
    "ryan": "Ryan Van Stonebraker",
    "george": "george",
    "matt": "Matt Perry",
    "tyler": "Tyler Chase",
    "harry": "harry",
    "hermione": "hermione",
    "ron": "ron",
    "andrew": "Andrew Van Adler",
    "trump": "Donald Julio Trump",
    "izac": "Izac Lorimer"
}

lucidDream = generator.LucidDream(
    characters=list(characters.keys()).copy(),
    response_length=40
)

load_dotenv()
TOKEN = os.getenv('DISCORD-BOT-LD-TOKEN')

client = discord.Client()

save_counter = {}

async def write_history(message):
    with open(f"history/{message.guild.name}.txt", "w") as discord_writer:
            async for message in message.channel.history(limit=100000):
                discord_writer.write(f"{message.author.display_name}: {message.content}\n")

@client.event
async def on_message(message):
    global save_counter
    if message.author == client.user:
        return

    save_counter[message.guild.name] = 1 if message.guild.name not in save_counter else save_counter[message.guild.name] + 1

    amended_characters = {guild_member.display_name: guild_member.display_name for guild_member in message.guild.members}
    amended_characters.update(characters)

    if message.content.startswith("!save"):
        await write_history(message)
        return
    elif message.content.startswith("!breakdown"):
        character = message.content.replace("!breakdown", "").strip()
        await message.guild.me.edit(nick=character)
        await message.channel.send(lucidDream.get_emotional_profile(character, message.guild.name))
        return

    for character, real_character in amended_characters.items():
        if character.lower() in message.content.lower():
            history = await message.channel.history(limit=50).map(lambda old_message: (old_message.author.display_name, old_message.content)).flatten()
            # await message.channel.send(f"{character}: let me think...")
            await message.guild.me.edit(nick=real_character)
            lucidDream.characters = [real_character]

            # channel_history = await message.channel.history(limit=31).flatten()
            # print("CHANNEL HISTORY", channel_history)
            print(f"{real_character} is responding")
            async with message.channel.typing():
                response = lucidDream.start_conversation(history, filtered=True)

                for member in message.guild.members:
                    response = response.replace(member.display_name, member.mention) if member.display_name in response else response
                        # print(member.nick, member.display_name)
                # for _, character in characters.items():
                #     if character in response:
                #         member_mention = discord.utils.get(message.guild.members, name=character)
                #         member_mention = member_mention.mention if member_mention else character
                #         response = response.replace(character, member_mention)
                await message.channel.send(response)

    if save_counter[message.guild.name] > 5:
        save_counter[message.guild.name] = 0
        await write_history(message)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)