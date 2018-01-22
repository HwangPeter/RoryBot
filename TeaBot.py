#!/usr/bin/python3
import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
from datetime import datetime

bot = commands.Bot(description="Tea's productivity bot", command_prefix="!", pm_help = True)

@bot.event
async def on_ready():
    print('Logged in as '+bot.user.name+' (ID:'+bot.user.id+') | Connected to '+str(len(bot.servers))+' servers | Connected to '+str(len(set(bot.get_all_members())))+' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('--------')
    print('Use this link to invite {}:'.format(bot.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(bot.user.id))
    print('--------')
    server = bot.get_server('392806051507994624')
    tea = discord.utils.get(server.members, id = '212404022697656321')
    #await bot.send_message(tea, "Hello. I am online.") #TODO: Uncomment this line.

@bot.command(name = "hello", pass_context = True)
async def hello(ctx):
    time = int(datetime.now().strftime("%H"))
    if time < 12 and time >= 6:
        await bot.say("Good morning human.")
    elif time < 16 and time >= 12:
        await bot.say("Good afternoon. Did you manage to wake up this morning?")
    elif time < 21 and time >= 16:
        await bot.say("Good evening. A cup of tea sounds lovely right now.")
    else:
        if time == 0:
            time = "midnight"
        elif time > 12:
            await bot.say("Is it " +str(time-12)+ " already? Night time is charming, isn't it?")
        else:
            await bot.say("Is it " +str(time)+ " already? Night time is charming, isn't it?")

@bot.command(name = "designstorm", pass_context = True)
async def designstorm(ctx):
    """ !designstorm Creates timers and categories and allows for notetaking. """
    bot_id = "401288936946925568"
    time_left_alert = 60 #Amount of time that is left when bot warns user. In seconds.
    categories_dict = { #Feel free to add more default categories. Follow the format.
    "1":"Colors",
    "2":"Typography",
    "3":"Iconography",
    "4":"Components"
    }
    prompt = """Alright, let's start a brainstorm for your design. Separate the categories you'd like to include with commas.
    *Ex. <custom category 1, all, custom category 2>*\n\n"""
    index = 1
    for category in categories_dict:
        prompt += str(index) + ". " + categories_dict[category] + "\n"
        index +=1
    prompt += "Or you can add your own category to the list directly.\n"
    await bot.say(prompt)

    categories_msg = await bot.wait_for_message(author = ctx.message.author)
    categories = []
    categories = await get_categories(categories, categories_msg)

    #Translates numbers from prompt into their respective category.
    index = 0
    for category in categories:
        if category.isdigit():
            categories[index] = categories_dict[category]
            index += 1
        elif category.casefold() == "all":
            all_list = list(categories_dict.values())
            categories = categories[:index] + all_list + categories[index+1:]
            index += len(all_list)
        else:
            index += 1
    categories = list(dict.fromkeys(categories))
    print(categories)

    #Some setup, prompts user for whether they want same time for each category or different times.
    same_time_choice = False
    if len(categories) > 1:
        await bot.say("Very well. Do you want the same amount of time for every category?")
        while True:
            time_choice_msg = await bot.wait_for_message(author = ctx.message.author)
            time_length = -1
            if "y" in time_choice_msg.content.casefold():
                same_time_choice = True
                await bot.say("Alright, let's do the same time for every category. How many minutes each? 0 for untimed.")
                time_length = await get_time_length(ctx)
                break
            elif "n" in time_choice_msg.content.casefold():
                await bot.say("Alright, let's do different times for each section. How many minutes would you like for " + categories[0] + "? 0 for untimed.")
                time_length = await get_time_length(ctx)
                break
            else:
                await bot.say("Not sure what you mean. Do you want the same amount of time for every category?")
    else:
        await bot.say("How many minutes would you like for " + categories[0] + "? 0 for untimed.")
        time_length = await get_time_length(ctx)

    #Designstorm begins here.
    notes = ""
    await bot.say("Finally. Now we can get started!")
    for category in categories:
        if same_time_choice == False and category is not categories[0]:
            await bot.say("Your time is up, human.")
            await bot.say("How many minutes for " + category + "?")
            time_length = await get_time_length(ctx)
        if time_length == 0: # Untimed designstorm section.
            await bot.say("Alright, let's do **" + category + "**. Say done whenever you're finished with this section.")
            while True:
                done_msg = await bot.wait_for_message(author = ctx.message.author)
                if done_msg.content.casefold() == "done":
                    await bot.delete_message(done_msg)
                    break
                else:
                    done_msg = await bot.wait_for_message(author = ctx.message.author)
        else: #Timed designstorm section.
            if time_length == 60:
                await bot.say("Alright, let's do **" + category + "**. You have " + str(int(time_length/60)) + " minute. Good luck!")
            else:
                await bot.say("Alright, let's do **" + category + "**. You have " + str(int(time_length/60)) + " minutes. Good luck!")
            if time_length > 180:
                await asyncio.sleep(time_length - time_left_alert)
                await bot.say("Tick-tock, you have 1 minute left human. Start wrapping it up.")
                await asyncio.sleep(time_left_alert)
            else:
                time_left_alert = 15
                await asyncio.sleep(time_length - time_left_alert)
                await bot.say("Tick-tock, you have 15 seconds left human. Start wrapping it up.")
                await asyncio.sleep(time_left_alert)

        #At the end of each category, bot grabs all messages from user until it reaches a previous prompt by the bot.
        botto = discord.utils.get(ctx.message.server.members, id = bot_id)
        notes_found = False
        category_notes = ""
        async for message in bot.logs_from(ctx.message.channel, limit = 100):
            if message.author == botto and category.casefold() in message.content.casefold():
                break
            elif message.author == ctx.message.author:
                notes_found = True
                category_notes = message.content + "\n" + category_notes
        if notes_found == True:
            if category == "Colors":
                category_notes = "🎨 **" + category + "**: \n" + category_notes
                notes += category_notes + "\n"
            elif category == "Typography":
                category_notes = "✒ **" + category + "**: \n" + category_notes
                notes += category_notes + "\n"
            elif category == "Iconography":
                category_notes = "🔰 **" + category + "**: \n" + category_notes
                notes += category_notes + "\n"
            elif category == "Components":
                category_notes = "✨ **" + category + "**: \n" + category_notes
                notes += category_notes + "\n"
            else:
                category_notes = "**" + category + "**: \n" + category_notes
                notes += category_notes + "\n"
    if notes:
        await bot.say("We're done now. These are the notes I saved for you:\n\n" + notes)
    else:
        await bot.say("We're done now.")

async def get_time_length(ctx):
    """ Checks against anything other than numbers. Multiplies answer by 60 to return minutes. """
    while True:
        time_length_msg = await bot.wait_for_message(author = ctx.message.author)
        if time_length_msg.content.isdigit():
            return (int(time_length_msg.content) * 60)
        else:
            await bot.say("I'm not even from here but I know what an integer is. So should you.")

async def get_categories(categories, categories_msg):
    """ Takes user's desired categories answer and returns a list object containing each category. """
    content = categories_msg.content
    pos_end = content.find(',')
    pos_start = 0
    if pos_end == -1:
        category = await remove_spaces(content)
        categories.append(content)
        return categories
    else: # more than 1 category
        while pos_end != -1 and pos_end != 0:
            category = await inc_between(content, pos_start, pos_end)
            category = await remove_spaces(category)
            print("category is: " + category)
            categories.append(category)
            content = content[pos_end+1:]
            pos_end = content.find(',')
        if content:
            category = await remove_spaces(content)
            print("category is: " + category)
            categories.append(category)
        return categories

async def inc_between(string, a, b):
    """ Returns string between indexes 'a' and 'b'. INCLUDES characters at indexes 'a' and 'b'. """
    if a == -1: return ""
    if b == -1: return ""
    if a >= b: return ""
    return string[a:b]

async def remove_spaces(string):
    """ Removes spaces at the beginning and end of a string """
    index = 0
    while string[index] == " ":
        index += 1
    string = string[index:]
    index = len(string) - 1
    while string[index] == " ":
        index -= 1
    string = string[:index + 1]
    return string

@bot.command(name = "multiply", pass_context = True)
async def multiply(ctx):
    """ !multiply a * b or !multiply a x b where a and b are integers."""
    if len(ctx.message.content) > len("!multiply ") and "x" in ctx.message.content.casefold():
        content = ctx.message.content[len("!multiply "):].replace(" ", "")
        #a and b are the numbers being multiplied
        a = content[:content.find("x")]
        b = content[content.find("x")+1:]
        await bot.say("Your answer is: " + str(int(a)*int(b)))
    elif len(ctx.message.content) > len("!multiply ") and "*" in ctx.message.content:
        content = ctx.message.content[len("!multiply "):].replace(" ", "")
        #a and b are the numbers being multiplied
        a = content[:content.find("*")]
        b = content[content.find("*")+1:]
        await bot.say("Your answer is: " + str(int(a)*int(b)))
    else:
        await bot.say("Ya did it wrong.")


@bot.command(name = "dimensions", pass_context = True)
async def dimensions(ctx):
    """ !dimensions ax + by = z where a > b and a,b,z are integers. """
    temp_ans = 0
    x = 0
    y = 0
    found = False
    answers = ""
    content = ctx.message.content[len("!dimensions "):].replace(" ", "").casefold()
    if len(ctx.message.content) > len("!dimensions ") and "x" in content and "y" in content:
        a, b, ans = await get_values(content)
        if a and b and ans:
            temp_ans = ans
            while temp_ans > 0:
                if temp_ans%b == 0:
                    y = temp_ans/b
                    answers += "x = " + str(x) + ", y = " + str(int(y)) + "\n"
                x += 1
                temp_ans -= a
            try:
                await bot.say(answers)
            except discord.errors.HTTPException:
                #400
                await bot.say("Couldn't find a single solution.")
            except:
                await bot.say("Can't say.")

    else:
        await bot.say("Ya did it wrong.")


async def get_values(content):
    a = content[:content.find("x")]
    if not a.isdigit():
        await bot.say("a has to be an integer.")
        return 0, 0, 0
    b = content[content.find("+")+1:content.find("y")]
    if not b.isdigit():
        await bot.say("b has to be an integer.")
        return 0, 0, 0
    ans = content[content.find("=")+1:]
    if not ans.isdigit():
        await bot.say("z has to be an integer.")
        return 0, 0, 0
    return int(a), int(b), int(ans)


@bot.command(name = "shutdown", pass_context = True)
async def shutdown(ctx):
    """ !shutdown Turns off the bot. """
    server = bot.get_server('392806051507994624')
    tea = discord.utils.get(server.members, id = '212404022697656321')
    schlong = discord.utils.get(server.members, id = '217513859412525057')
    if ctx.message.author == tea or ctx.message.author == schlong:
        await bot.say("Is it time to go? Til next time human.")
        bot.logout()
        await asyncio.sleep(5)
        exit()
    else:
        await bot.say("How dare you?")

@bot.command(name = "timer", pass_context = True)
async def time(ctx):
    """ !timer time length, timer subject(optional) """
    time_left_alert = 60 #Amount of time that is left when bot warns user. In seconds.
    if len(ctx.message.content) > len("!timer ") and any(char.isdigit() for char in ctx.message.content): # Check for any information after the command
        #Removing spaces, and uppercases and splices off the command from message.
        content = ctx.message.content[len("!timer "):].casefold()
        subject = ""
        if "," in content:
            try: # This try block separates timer information from timer subject
                time, subject = content.split(",")
            except ValueError:
                await bot.say("Ya dun goofed.")
        else:
            time = content
        time = time.replace(" ", "")
        subject = subject.strip()
        time = await get_time(time)
        if time > 0:
            if subject:
                await bot.say("⏰ Okay, your *" + subject + "* timer is starting now!")
                await asyncio.sleep(time)
                await bot.say("⏰ <@" + ctx.message.author.id + '> Your timer for *' + subject + '* is up!')
            else:
                await bot.say("⏰ Okay, your timer is starting now!")
                await asyncio.sleep(time)
                await bot.say("⏰ <@" + ctx.message.author.id + "> Your timer is up!")
        else:
            await bot.say("Ya dun goofed.")
    else:
        await bot.say("Ya dun goofed.")


async def get_time(time):
    hours = "0"
    minutes = "0"
    seconds = "0"
    for index, char in enumerate(time):
        if char == "h" and time[index-1].isdigit(): #contains hours
            index2 = index-1
            while time[index2].isdigit():
                index2 -= 1
            hours = time[index2+1:index]
            break
    for index, char in enumerate(time):
        if char == "m" and time[index-1].isdigit(): #contains minutes
            index2 = index-1
            while time[index2].isdigit():
                index2 -= 1
            minutes = time[index2+1:index]
            break
    for index, char in enumerate(time):
        if char == "s" and time[index-1].isdigit(): #contains seconds
            index2 = index-1
            while time[index2].isdigit():
                index2 -= 1
            seconds = time[index2+1:index]
            break
    print("HOURS: " + hours) #TODO:RAT
    print("MINUTES: " + minutes)
    print("SECONDS: " + seconds)
    return (int(hours)*3600 + int(minutes) * 60 + int(seconds))



bot.run('token')
