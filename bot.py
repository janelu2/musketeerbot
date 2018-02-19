import discord, logging, json, re
from discord.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import delete,increment

description = '''Basic bot used to do fun things on Roy's Boy Toys '''
bot = commands.Bot(command_prefix='!', description=description)
db = TinyDB('data.json')
Users = Query()

bot_info = json.load(open('bot_info.json'))
token = bot_info['token']

# Print the starting text
print('---------------')
print('Starting RoyBot...')
print('---------------')

logging.basicConfig(level=logging.INFO)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print('---------------')

@bot.listen()
async def on_message(message):
    """Roy's "my best" joke; see roy_jokes.txt"""
    joke_setup_pattern = r"^(.*)[wW](hat|tf)(.*)(did|have|is|are|am)(.*)(doing|going to do|do|done)(.*)$"
    match = re.match(joke_setup_pattern, message.content)
    if match:
        if "am I" in str(message.content) or "am i" in str(message.content):
            await bot.send_message(message.channel, "Your best")
        elif bot.user.mentioned_in(message) and ("you doing" in str(message.content) or "u doing" in str(message.content)):
            # Note that members are used for server stuff and Users are used for PRIVATE messages
            # bot user info is under bot.user
            await bot.send_message(message.channel, "My best")
        else:
            await bot.send_message(message.channel, "Their best")

@bot.listen()
async def on_message(message):
    """RoyBot is afraid of possums"""
    if "possum" in str(message.content).lower():
        await bot.send_message(message.channel, "::ehuuuuu:: I'm brave when it counts!!")

"TODO: MAKE THIS USE RDS"
@bot.command()
async def shame():
    """Says when a member joined."""
    bot_info['grains'] += 1
    numgrains = bot_info['grains']
    await bot.say("1 grain of sand added to @DirtyGrundler#6579's jar of shame (currently " + numgrains + " grains of sand)")

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

bot.run(token)
