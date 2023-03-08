# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# You can find misc modules, which dont fit in anything xD
""" Userbot module for other small commands. """

import sys
import random
from time import sleep

from asyncio import CancelledError
from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, bot
from userbot.events import register
from os import environ

shutDown = False

@register(outgoing=True, pattern="^.random")
async def randomise(items):
    """ For .random command, get a random item from the list of items. """
    if environ.get("isSuspended") == "True":
        return
    itemo = (items.text[8:]).split()
    if len(itemo) == 1:
        print(itemo[0])
        number = int(random.random() * float(itemo[0]))
        print(number)
        await items.edit("**Random number**: `" + str(number) + '`')
        return
    if len(itemo) == 0:
        await items.edit("`1 or more items are required! Check "
                         ".help random for more info.`")
        return

    await items.edit("**Query: **\n`" + items.text[8:] + "`\n**Output: **\n`" +
                     random.choice(itemo) + "`")


@register(outgoing=True, pattern="a^.sleep( [0-9]+)?$")
async def sleepybot(time):
    """ For .sleep command, let the userbot snooze for a few second. """
    if environ.get("isSuspended") == "True":
        return
    if " " not in time.pattern_match.group(1):
        await time.reply("Syntax: `.sleep [seconds]`")
    else:
        counter = int(time.pattern_match.group(1))
        await time.edit("`I am sulking and snoozing....`")
        sleep(2)
        if BOTLOG:
            await time.client.send_message(
                BOTLOG_CHATID,
                "You put the bot to sleep for " + str(counter) + " seconds",
            )
        sleep(counter)


@register(outgoing=True, pattern="^\.shutdown$")
async def killdabot(event):
    """ For .shutdown command, shut the bot down."""
    await event.edit("`Goodbye *Windows XP shutdown sound*....`")
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "#SHUTDOWN \n"
                                        "Bot shut down")
    open("./temp.txt", 'w').close
    f = open("./temp.txt", "w+")
    f.write("False")
    global shutDown
    shutDown = True
    try:
      await bot.disconnect()
    except CancelledError:
      pass
    except Exception as e:
      print(f"Error while shutdown: {e}")


@register(outgoing=True, pattern="^\.restart$")
async def killdabot(event):
    await event.edit("`BRB... *PornHub intro*`")
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "#RESTART \n"
                                        "Bot Restarted")
    open("./temp.txt", 'w').close
    f = open("./temp.txt", "w+")
    f.write("True")
    global shutDown
    shutDown = True
    try:
      await bot.disconnect()
    except CancelledError:
      pass
    except Exception as e:
      print(f"Error while restarting: {e}")

@register(outgoing=True, pattern="^.support$")
async def bot_support(wannahelp):
    """ For .support command, just returns the group link. """
    if environ.get("isSuspended") == "True":
        return
    await wannahelp.edit("Link Portal: @userbot_support")


@register(outgoing=True, pattern="^.repo$")
async def repo_is_here(wannasee):
    """ For .repo command, just returns the repo URL. """
    if environ.get("isSuspended") == "True":
        return
    await wannasee.edit("https://github.com/PolisanTheEasyNick/Telegram-UserBot/")

@register(outgoing=True, pattern="^.suspend")
async def sus(susp):
    environ["isSuspended"] = "True"
    await susp.edit("**Bot has been suspended...**")

CMD_HELP.update({"misc": ["Misc",
    " - `.random <item1> <item2> ... <itemN>`: Get a random item from the list of items.\n"
    " - `.sleep <secs>`: Paperpane gets tired too. Let yours snooze for a few seconds.\n"
    " - `.shutdown`: Sometimes you need to turn Paperplane off. Sometimes you just hope to"
    "hear Windows XP shutdown sound... but you don't.\n"
    " - `.support`: If you need more help, use this command.\n"
    " - `.repo`: Get the link of the source code of Paperplane in GitHub.\n"]
})
