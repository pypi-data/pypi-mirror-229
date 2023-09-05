# TeLLMgramBot
The basic goal of this project is to create a bridge between a Telegram Bot and a Large Langage Model (LLM), like ChatGPT.

## Telegram Bot + LLM Encapsulation
* The Telegram interface handles special commands, especially on some basic "chatty" prompts and responses that don't require LLM, like "Hello".
* The more dynamic conversation gets handed off to the LLM to manage prompts and responses, and Telegram acts as the interaction broker.
* The bot can also interpret URLs. Pass the URL [in brackets] and mention what you want the bot to do with it.
  * Example: "What do you think of this article? [https://some_site/article]"

## Why Telegram?
Using Telegram as the interface not only solves "exposing" the interface, but gives you boadloads of interactivity over a standard Command Line interface, or trying to create a website with input boxes and submit buttons to try to handle everything:
1. Telegram already lets you paste in verbose, multiline messages.
2. Telegram already lets you paste in pictures, videos, links, etc.
3. Telegram already lets you react with emojis, stickers, etc.

## API Keys
To function, the bot requires three API keys:
* [OpenAI](https://platform.openai.com/overview) - Drives the actual GPT AI.
* [BotFather](https://t.me/BotFather) - Helps create a new Telegram bot and provide its API.
* [VirusTotal](https://www.virustotal.com/gui/home/) - Performs safety checks on URLs.

## Bot Setup
1. To initialize the bot, install via PIP (`pip install TeLLMgramBot`) and then import into your project.
2. Instantiate the bot by passing in various configuration pieces needed. Use [OpenAI Playground](https://platform.openai.com/playground) to test more your prompt.
   ```
   telegram_bot = TeLLMgramBot.TelegramBot(
       bot_username   = <Bot username like 'friendly_bot'>,
       bot_nickname   = <Bot nickname like 'Botty'>,
       bot_initials   = <Bot initials like 'FB'>,
       bot_owner      = <Bot owner's Telegram username>,
       chatmodel      = <ChatGPT model like 'gpt-3.5-turbo'>,
       persona_name   = <Bot name like 'Friendly Bot'>,
       persona_prompt = <System prompt summarizing bot personality>,
       persona_temp   = <LLM value [0-2] being factual vs. creative>
   )
   ```
3. Run by calling:
   ```
   telegram_bot.start_polling()
   ```
4. Once you see `TeLLMgramBot polling...`, the bot is online in Telegram. Initiate a conversation there by passing the `/start` command.
   * **NOTE**: The bot will only respond to the `/start` command coming from the `bot_owner` username. 
