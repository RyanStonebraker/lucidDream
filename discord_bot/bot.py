import os
import discord
import contextlib

from dotenv import load_dotenv

import generator
import pandas as pd
import os
import random

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
    response_length=40,
    run_name="small_uafcsc_better"
)

load_dotenv()
TOKEN = os.getenv('DISCORD-BOT-LD-TOKEN')

client = discord.Client()

save_counter = {}
filter_users = {}
continue_talking = False

async def write_history(message):
    with open(f"history/{message.guild.name}.txt", "w") as discord_writer:
            async for message in message.channel.history(limit=100000):
                discord_writer.write(f"<|start_text|>{message.author.display_name}: {message.content}<|end_text|>\n")

@client.event
async def on_message(message):
    global save_counter
    global continue_talking
    if message.author == client.user and "!free" in message.content and "Commands:" not in message.content:
        continue_talking = True
    if not message.content.startswith("!") and message.author == client.user:
        return

    save_counter[message.guild.name] = 1 if message.guild.name not in save_counter else save_counter[message.guild.name] + 1

    amended_characters = {guild_member.display_name: guild_member.display_name for guild_member in message.guild.members}
    amended_characters.update(characters)

    if f"{message.guild.name}.csv" in os.listdir("characters"):
        with open(f"characters/{message.guild.name}.csv", "r") as character_reader:
                amended_characters = {line.split(":")[0].strip(): line.split(":")[-1].strip() for line in character_reader.readlines()}
    else:
        with open(f"characters/{message.guild.name}.csv", "w") as character_writer:
            for character, full_name in amended_characters.items():
                character_writer.write(f"{character}:{full_name}\n")
    
    lucidDream.characters = list(amended_characters.values())

    if message.content.startswith("!save"):
        await write_history(message)
        return
    elif message.content.startswith("!breakdown"):
        character = message.content.replace("!breakdown", "").strip()
        await message.guild.me.edit(nick=character)
        await message.channel.send(lucidDream.get_emotional_profile(character, message.guild.name))
        return
    elif message.content.startswith("!users"):
        await message.channel.send(str(amended_characters))
        return
    elif message.content.startswith("!add"):
        character = [character.strip() for character in message.content.replace("!add", "").split(":")]
        with open(f"characters/{message.guild.name}.csv", "a") as character_writer:
            character_writer.write(f"{character[0]}:{character[-1]}\n")
        amended_characters[character[0]] = character[-1]
        return
    elif message.content.startswith("!remove"):
        remove_character = message.content.replace("!remove", "").strip()
        with open(f"characters/{message.guild.name}.csv", "w") as character_writer:
            for character, full_name in amended_characters.items():
                if remove_character != character and remove_character != full_name:
                    character_writer.write(f"{character}:{full_name}\n")
        del amended_characters[remove_character]
        return
    elif message.content.startswith("!label"):
        emotion = message.content.replace("!label", "").strip()
        async for old_message in message.channel.history(limit=2):
            if old_message.content == message.content:
                continue
            with open(f"history/{message.guild.name}_emotion.txt", "a") as emotion_writer:
                old_content = old_message.content.replace('\n', '\\n')
                emotion_writer.write(f"{emotion}, {old_content}\n")
        return
    elif message.content.startswith("!models"):
        available_models = "\n\t".join(os.listdir("checkpoint"))
        await message.channel.send(f"Currently using: {lucidDream.run_name}\nAvailable:\n\t{available_models}")
        return
    elif message.content.startswith("!useModel"):
        model = message.content.replace("!useModel", "").strip()
        if model in os.listdir("checkpoint"):
            lucidDream.run_name = model
            await message.channel.send(f"Switched to {model}")
        return
    elif message.content.startswith("!shutup"):
        continue_talking = False
        return
    elif message.content.startswith("!help"):
        await message.channel.send(
            "Commands:\n" +
            "**!save <no args>**: save the current chat history to a file on Ryan's computer.\n" +
            "**!breakdown <exact name>**: gives an emotional breakdown of the user based on their past conversation.\n" +
            "**!users <no args>**: returns a list of users and aliases for users that, if mentioned, will trigger the bot. Format: alias:username\n"
            "**!add <alias:username>**: Adds an alias/username as a trigger word for the bot. passing one argument is equivalent to saying username:username (ex. !add user == !add user:user).\n" +
            "**!remove <alias>**: Removes an alias as a trigger word for the bot.\n" +
            "**!label <emotion>**: Label the past message sent as a certain emotion (doesn't have to be a bot's last message). This helps the model learn emotions better and get better profiles.\n" +
            "**!models <no args>**: Show a list of available models to switch the chatbot to.\n" +
            "**!useModel <model_name>**: Switch the chatbot to use the model specified.\n" +
            "**!shutup <no args>**: If the model manages to say \"!free\", it will no longer be bound to waiting for trigger words to respond and will be able to talk freely. !shutup will end this.\n" +
            "**NOTE:** The AI model is free to use any of the above commands as well and they will all work for it.\n"
        )
        return


    for character, real_character in amended_characters.items():
        if character.lower() in message.content.lower() or continue_talking:
            character = random.choice(list(amended_characters.values())) if continue_talking else character
            history = await message.channel.history(limit=50).map(lambda old_message: (old_message.author.display_name, old_message.content)).flatten()
            await message.guild.me.edit(nick=real_character)
            lucidDream.characters = [real_character]

            print(f"{real_character} is responding")
            async with message.channel.typing():
                response = lucidDream.start_conversation(history, filtered=True)

                for member in message.guild.members:
                    response = response.replace(member.display_name, member.mention) if member.display_name in response else response
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