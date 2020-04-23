import random
import re
import os
import asyncio
import discord


class ResponseClient:
    def __init__(self, lucid_dream, model="", characters={}):
        self.lucid_dream = lucid_dream
        self.characters = characters
        self.continue_talking = False
        self.allow_mentions = True
        self.save_counter = 0
        self.model = model if model else lucid_dream.run_name

        self.game_mode = False
        self.tweets = []
        self.last_message = ""

        self.knight_role = "king_george"
    
    def load_characters(self, message):
        if f"{message.guild.name}_{message.channel.name}.csv" in os.listdir("characters"):
            with open(f"characters/{message.guild.name}_{message.channel.name}.csv", "r") as character_reader:
                self.characters = {line.split(":")[0].strip(): line.split(":")[-1].strip() for line in character_reader.readlines()}
        else:
            self.characters.update({guild_member.display_name: guild_member.display_name for guild_member in message.guild.members})
            with open(f"characters/{message.guild.name}_{message.channel.name}.csv", "w") as character_writer:
                for character, full_name in self.characters.items():
                    character_writer.write(f"{character}:{full_name}\n")

    def get_parameter_string(self, message, command):
        return message.content.replace(command, "").strip()

    async def show_characters(self, message):
        await message.channel.send("Users:\n" + "\n\t".join([f"{character}: {full_name}" for character, full_name in self.characters.items()]))

    async def add_character(self, message):
        character = self.get_parameter_string(message, "!add")
        character, full_name = (character[:character.find(":")], character[character.find(":")+1:]) if character.find(":") > 0 else (character, character)
        self.characters[character] = full_name
        with open(f"characters/{message.guild.name}_{message.channel.name}.csv", "w") as character_writer:
            for character, full_name in self.characters.items():
                character_writer.write(f"{character}:{full_name}\n")

    async def remove_character(self, message):
        remove_character = self.get_parameter_string(message, "!remove")
        if remove_character not in self.characters.keys() and remove_character not in self.characters.values():
            return
        with open(f"characters/{message.guild.name}_{message.channel.name}.csv", "w") as character_writer:
            for character, full_name in self.characters.items():
                if character != remove_character and full_name != remove_character:
                    character_writer.write(f"{character}:{full_name}\n")
        self.characters = []
        self.load_characters(message)

    async def write_history(self, message):
        with open(f"history/{message.guild.name}_{message.channel.name}.txt", "w") as discord_writer:
            async for message in message.channel.history(limit=100000):
                discord_writer.write(f"<|start_text|>{message.author.display_name}: {message.content}<|end_text|>\n")

    async def get_history(self, message):
        if "sysadmin" in self.lucid_dream.run_name:
            history = [(message.author.display_name, message.content.strip())]
        else:
            history = await message.channel.history(limit=30).map(lambda old_message: (old_message.author.display_name, old_message.content)).flatten()
        return history

    def get_trump_tweets(self):
        if not self.tweets:
            with open("../corpora/trump.txt", "r") as trump_reader:
                self.tweets = [tweet.strip() for tweet in re.findall(r"<|start_text|>Donald Trump:(.+?)<|end_text|>", trump_reader.read()) if tweet.strip()]
        return self.tweets

    async def answer(self, message):
        answer = self.get_parameter_string(message, "!answer")
        if not self.game_mode:
            await message.channel.send("Start a game first!")
        
        self.game_mode = False
        await message.channel.send(f"{message.author.display_name} {'wins' if self.last_message.lower() == answer else 'loses'}! The last message was sent by: {self.last_message}.")

    async def trump_or_ai(self, message):        
        self.game_mode = True
        history = await self.get_history(message)
        await message.guild.me.edit(nick="Donald Trump")

        self.last_message = random.choice(["ai", "trump"])
        async with message.channel.typing():
            response = random.choice(self.get_trump_tweets())
            if self.last_message == "trump":
                await asyncio.sleep(random.randrange(7,15))
            else:
                response = self.lucid_dream.start_conversation([("Donald Trump", response)], run_name=self.model, character="Donald Trump", characters=list(self.characters.keys())).strip()
            response = re.sub(r"(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?", "", response)
            await message.channel.send(response)

    async def label_emotion(self, message):
        emotion = message.content.replace("!label", "").strip()
        async for old_message in message.channel.history(limit=2):
            if old_message.content == message.content:
                continue
            with open(f"history/{message.guild.name}_{message.channel.name}_emotion.txt", "a") as emotion_writer:
                old_content = old_message.content.replace('\n', '\\n')
                emotion_writer.write(f"{emotion}, {old_content}\n")

    async def breakdown_character(self, message):
        character = self.get_parameter_string(message, "!breakdown")
        await message.guild.me.edit(nick="therapist")
        await self.write_history(message)
        await message.channel.send(self.lucid_dream.get_emotional_profile(character, f"history/{message.guild.name}_{message.channel.name}.txt"))

    async def switch_model(self, message):
        model = self.get_parameter_string(message, "!useModel")
        if model in os.listdir("checkpoint"):
            self.model = model
            await message.channel.send(f"Switched to {model}")

    async def show_models(self, message):
        available_models = "\n\t".join(os.listdir("checkpoint"))
        await message.channel.send(f"Currently using: {self.lucid_dream.run_name}\nAvailable:\n\t{available_models}")

    async def modify_temperature(self, message):
        temperature = self.get_parameter_string(message, "!temperature")
        if temperature:
            try:
                self.lucid_dream.temperature = float(temperature)
            except:
                pass
        await message.channel.send(f"Temperature: {self.lucid_dream.temperature}")

    async def knight(self, message, client):
        user = self.get_parameter_string(message, "!knight")
        for member in message.guild.members:
            if member.display_name == user:
                print(f"Knighting {member.display_name}")
                await client.add_roles(member, discord.utils.get(message.server.roles, name=self.knight_role))

    def start_talking(self):
        self.continue_talking = True

    async def stop_talking(self, message):
        if self.continue_talking:
            self.continue_talking = False
            await message.channel.send(f"Stopped talking freely")

    async def respond(self, history, message, character):
        async with message.channel.typing():
            response = self.lucid_dream.start_conversation(history, run_name=self.model, character=character, characters=list(self.characters.keys())).strip()
            if not response:
                response = self.lucid_dream.start_conversation(history, random_seed=True, run_name=self.model, character=character, characters=list(self.characters.keys())).strip()
            for member in message.guild.members:
                if self.allow_mentions:
                    response = re.sub(r"\b({})\b".format(member.display_name), member.mention, response)
                else:
                    response = response.replace(member.mention, "@member")
            try:
                await message.channel.send(response)
            except Exception as err:
                print(err, f"\nRAW: {response}")
                await message.channel.send("I HAVE FAILED AT RESPONDING. YOU BROKE ME.")

    async def respond_on_character(self, message):
        for character, real_character in self.characters.items():
            if character.lower() in message.content.lower() or self.continue_talking:
                real_character = random.choice(list(self.characters.values())) if self.continue_talking else character
                history = await self.get_history(message)
                await message.guild.me.edit(nick=real_character)

                print(f"{real_character} is responding")
                await self.respond(history, message, real_character)

                self.save_counter += 1
                if self.save_counter > 5:
                    self.save_counter = 0
                    await self.write_history(message)
                break

    async def send_help(self, message):
        await message.channel.send(
            "Commands:\n" +
            "**!save <no args>**: save the current chat history to a file on the server.\n" +
            "**!breakdown <exact name>**: gives an emotional breakdown of the user based on their past conversation.\n" +
            "**!users <no args>**: returns a list of users and aliases for users that, if mentioned, will trigger the bot. Format: alias:username\n"
            "**!add <alias:username>**: Adds an alias/username as a trigger word for the bot. passing one argument is equivalent to saying username:username (ex. !add user == !add user:user).\n" +
            "**!remove <alias>**: Removes an alias as a trigger word for the bot.\n" +
            "**!label <emotion>**: Label the past message sent as a certain emotion (doesn't have to be a bot's last message). This helps the model learn emotions better and get better profiles.\n" +
            "**!models <no args>**: Show a list of available models to switch the chatbot to.\n" +
            "**!useModel <model_name>**: Switch the chatbot to use the model specified.\n" +
            "**!shutup <no args>**: If the model manages to say \"!free\", it will no longer be bound to waiting for trigger words to respond and will be able to talk freely. !shutup will end this.\n" +
            "**!temperature <optional temperature>**: Either see the current temperature level or set a new one.\n" +
            "**!trumpOrAI <no args>**: Try to guess whether the next message was sent by trump or an AI. Game ends when someone !answers trump or AI correctly.\n" +
            "**!answer <trump|ai>**: Ends the trumpOrAI game by answering.\n" +
            "**NOTE:** The AI model is free to use any of the above commands as well and they will all work for it.\n"
        )