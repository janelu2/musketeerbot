import discord, logging, json, re, random, asyncio, time
from discord.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import delete, increment

bot = commands.Bot(command_prefix='!', description='''Basic bot used to do fun things on Roy's Boy Toys ''')
db = TinyDB('db.json')
Database = Query()
random_length = 0
start_time = 0
emp_of_moment = ''
mutiny = False
mutiny_votes = []

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
    await start_tasks()

def get_server():
    """Get the server object that we are executing the bot in"""
    for i in bot.servers:
        if i.id == bot_info['serverid']:
            return i

def is_online_or_idle(user):
    """Check if a user is online"""
    if (str(user.status) == "online" or str(user.status) == "idle"):
        return True
    else:
        return False

def get_random_user(server):
    """Get a random user that is currently online (status = online)"""
    users = []
    num_users = 0
    for user in server.members:
        if user.bot is False:
            num_users += 1
            users.append(user)

    if num_users == 0:
        return bot.user
    else:
        return users[random.randint(0, num_users-1)]

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

async def role_assigner():
    """Assign the 'Employee of the moment' role to one user for a random amount
    of time, and then unassign and pass it on to someone else."""
    server = get_server()
    channel = server.get_channel(bot_info['channelid'])
    emp_role = discord.utils.get(server.roles, name="Employee of the moment")
    await remove_leftover_roles(server, emp_role)

    global random_length
    global emp_of_moment
    global start_time
    global mutiny

    while True:
        random_length = random.randint(1,86399)
        emp_of_moment = get_random_user(server)

        # if there's no one online, then the employee will be roybot for 30 mins
        if (emp_of_moment == bot.user):
            random_length = 1800

        await bot.add_roles(emp_of_moment, emp_role)

        # check if this new employee of the moment is due to mutiny
        if mutiny == True:
            while (emp_of_moment != last_employee):
                emp_of_moment = get_random_user(server)
            await bot.send_message(channel, "There has been a mutiny. Congratulations " + str(emp_of_moment) + "!")
            mutiny = False

        start_time = time.time()
        while True:
            if mutiny == True:
                last_employee = emp_of_moment
                break
            elif (time.time() - start_time) < random_length:
                await asyncio.sleep(3)
            else:
                break
        await bot.remove_roles(emp_of_moment, emp_role)

@bot.command()
async def check_role():
    """Check how much longer the current Employee of the Moment has until the moment is over."""
    global random_length
    hours = random_length//3600
    minutes = (random_length - 3600*hours)//60
    secs = random_length - (hours*3600) - (minutes*60)
    await bot.say(str(emp_of_moment) + "\'s moment will end at " +
        time.strftime('%I:%M %p', time.localtime(start_time + random_length)) +
        "! Their moment will last a total of " + str(hours) + " hours, " +
        str(minutes) + " mins, " + str(secs) + " secs.")

@bot.command(pass_context=True)
async def mutiny(ctx):
    """Commit mutiny"""
    global mutiny_votes
    global mutiny
    global emp_of_moment

    if ctx.message.author not in mutiny_votes:
        mutiny_votes.append(ctx.message.author)
        if (len(mutiny_votes) == 1):
            await bot.say("1 vote for mutiny")
        elif (len(mutiny_votes) == 2):
            await bot.say("2 votes for mutiny")
        elif (len(mutiny_votes) == 3):
            await bot.say("There has been a revolution. " + str(emp_of_moment) +
                "\'s moment has been officially murdered.")
    else:
        await bot.say("You have already voted")

    if (len(mutiny_votes) == 3):
        mutiny = True
        mutiny_votes[:] = []

@bot.command(pass_context=True)
async def check_mutiny(ctx):
    """Check on mutiny status"""
    global mutiny_votes

    if (len(mutiny_votes) == 0):
        await bot.say("The current rule is good and the people are happy -- no whispers of mutiny.")
    else:
        if (len(mutiny_votes) == 1):
            await bot.say("There is currently one mutineer.")
        else:
            await bot.say("There are currently " + str(len(mutiny_votes)) + " mutineers.")

if __name__ == '__main__':
    bot.run(token)
