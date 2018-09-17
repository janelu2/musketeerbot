import discord, logging, json, re, random, asyncio, time
from discord.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import delete, increment

bot = commands.Bot(command_prefix='!', description='''Basic bot used to do fun things on Roy's Boy Toys ''')
db = TinyDB('db.json')
Database = Query()

bot_info = json.load(open('bot_info.json'))
token = bot_info['token']

logging.basicConfig(level=logging.INFO)

# Print the starting text
print('---------------')
print('Starting RoyBot...')
print('---------------')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print('---------------')
    #await start_tasks()

def get_server():
    """Get the server object that we are executing the bot in"""
    for i in bot.servers:
        if i.id == bot_info['serverid']:
            return i

def is_online(user):
    """Check if a user is online"""
    if str(user.status) == "online":
        return True
    else:
        return False

def get_random_online_user(server):
    """Get a random user that is currently online (status = online)"""
    online_users = []
    num_users = 0
    for user in server.members:
        if is_online(user):
            num_users += 1
            online_users.append(user)

    return online_users[random.randint(0, num_users-1)]

async def remove_leftover_roles(server, role):
    """Sometimes when we start the bot up there might be some users that still
    have an old role such as 'Employee of the moment'. Here we remove the role
    from all users before executing role assignments."""
    for user in server.members:
        if role in user.roles:
            await bot.remove_roles(user, role)

async def start_tasks():
    '''This function will fire and forget a few methods that will run forever'''
    asyncio.ensure_future(loop_role_assigner())

async def loop_role_assigner():
    '''Run role assigner forever'''
    while True:
        await role_assigner()

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

@bot.command()
async def shame():
    """Increments number of grains of sand to Roy's Shame Jar."""
    db.update(increment('count'), Database.type == 'grains_of_sand')
    result = db.get(Database.type == 'grains_of_sand')
    await bot.say("1 grain of sand added to @DirtyGrundler#6579's jar of shame (currently " + str(result['count']) + " grains of sand)")

@bot.command()
async def jarstatus():
    """Notifies the status of Roy's Shame Jar."""
    result = db.get(Database.type == 'grains_of_sand')

    await bot.say("Currently " + str(result['count']) + " grains of sand!")
    if (result['count'] < 10):
        await bot.say("Not bad.")
    elif (result['count'] > 10 and result['count'] < 30):
        await bot.say("Be careful Roy...")
    else:
        await bot.say("Shameful :(")

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.command()
async def role_assigner():
    """Assign the 'Employee of the moment' role to one user for a random amount
    of time, and then unassign and pass it on to someone else."""
    server = get_server()
    channel = server.get_channel(bot_info['channelid'])
    emp_role = discord.utils.get(server.roles, name="Employee of the moment")
    await remove_leftover_roles(server, emp_role)

    while True:
        random_length = random.randint(1,30)
        user = get_random_online_user(server)
        await bot.add_roles(user, emp_role)
        await bot.send_message(channel, user.mention + " is now Employee of the Moment!")
        start_time = time.time()
        while True:
            if is_online(user) is False:
                break
            elif (time.time() - start_time) < random_length:
                asyncio.sleep(3)
            else:
                break
        await bot.remove_roles(user, emp_role)

if __name__ == '__main__':
    bot.run(token)
