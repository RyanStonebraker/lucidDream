import os
import discord
import contextlib
from dotenv import load_dotenv
import pandas as pd
import os
import random
import re
import asyncio

import generator
import responseClient

load_dotenv()
TOKEN = os.getenv('DISCORD-BOT-LD-TOKEN')

lucid_dream = generator.LucidDream(
    characters=[],
    response_length=40,
    run_name="small_uafcsc_better"
)

client = discord.Client()

sessions = {}

async def execute_commands(session, message):
    commands = {
        "save": session.write_history,
        "breakdown": session.breakdown_character,
        "users": session.show_characters,
        "add": session.add_character,
        "remove": session.remove_character,
        "label": session.label_emotion,
        "models": session.show_models,
        "useModel": session.switch_model,
        "shutup": session.stop_talking,
        "temperature": session.modify_temperature,
        "trumpOrAI": session.trump_or_ai,
        "channelOrAI": session.channel_or_ai,
        "answer": session.answer,
        "leaderboard": session.get_leaderboard,
        "help": session.send_help
    }
    for command_name, command in commands.items():
        if message.content.startswith(f"!{command_name}"):
            await command(message)
            break

@client.event
async def on_message(message):
    if message.guild.name not in sessions:
        sessions[message.guild.name] = responseClient.ResponseClient(lucid_dream)
        sessions[message.guild.name].load_characters(message)

    if message.author == client.user and "Commands:" not in message.content:
        if "!free" in message.content:
            sessions[message.guild.name].start_talking()
        elif message.content.startswith("!knight"):
            await sessions[message.guild.name].knight_user(message, client)

    if not message.content.startswith("!") and message.author == client.user:
        return

    if message.content.startswith("!"):
        await execute_commands(sessions[message.guild.name], message)
    else:
        await sessions[message.guild.name].respond_on_character(message)

@client.event
async def on_ready():
    print(f"Connected {client.user.name} - {client.user.id}\n------")
client.run(TOKEN)