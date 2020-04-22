# lucidDream
Dynamic Story Generation through directed chatbot interactions.

# Summary
This repository contains exploratory efforts towards controlling text generation using the GPT-2 model in a chatbot environment. It also houses an experimental Discord bot for interacting with simplified trained models.

## Dynamically Generating Stories
The `notebooks/Lucid Dream.ipynb` is the main notebook that aggregates the exploratory efforts from the others and provides the `start_conversation` function, which allows for a scene to by dynamically created and modified.

## Discord Bot
The Discord Bot located in `discord_bot/bot.py` serves as an interface for the gpt-2-simple library and aims to replicate some of the techniques used in the Lucid Dream notebook. The follow commands are available to use the bot:
```
!help:
    !save <no args>: save the current chat history to a local file on the server.
    !breakdown <exact name>: gives an emotional breakdown of the user based on their past conversation.
    !users <no args>: returns a list of users and aliases for users that, if mentioned, will trigger the bot. Format: alias:username
    !add <alias:username>: Adds an alias/username as a trigger word for the bot. passing one argument is equivalent to saying username:username (ex. !add user == !add user:user).
    !remove <alias>: Removes an alias as a trigger word for the bot.
    !label <emotion>: Label the past message sent as a certain emotion (doesn't have to be a bot's last message). This helps the model learn emotions better and get better profiles.
    !models <no args>: Show a list of available models to switch the chatbot to.
    !useModel <model_name>: Switch the chatbot to use the model specified.
    !shutup <no args>: If the model manages to say "!free", it will no longer be bound to waiting for trigger words to respond and will be able to talk freely. !shutup will end this.
    !temperature <optional temperature>**: Either see the current temperature level or set a new one.
    !trumpOrAI <no args>: Try to guess whether the next message was sent by trump or an AI. Game ends when someone guesses trump or AI correctly.

NOTE: The AI model is free to use any of the above commands as well and they will all work for it.
```
