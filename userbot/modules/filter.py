# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for filter commands """

from asyncio import sleep
from re import fullmatch, IGNORECASE, escape
from userbot import (BOTLOG, BOTLOG_CHATID, CMD_HELP, is_mongo_alive,
                     is_redis_alive)
from userbot.events import register
from userbot.modules.dbhelper import add_filter, delete_filter, get_filter


@register(incoming=True, disable_edited=True)
async def filter_incoming_handler(handler):
    """ Checks if the incoming message contains handler of a filter """
    try:
        if not (await handler.get_sender()).bot:
            if not is_mongo_alive() or not is_redis_alive():
                await handler.edit("`Database connections failing!`")
                return
            name = handler.raw_text
            filters = get_filters(handler.chat_id)
            if not filters:
                return
            for trigger in filters:
                pro = fullmatch(trigger.keyword, name, flags=IGNORECASE)
                if pro:
                    msg_o = await handler.client.get_messages(
                        entity=BOTLOG_CHATID, ids=int(trigger.f_mesg_id))
                    await handler.reply(msg_o.message, file=msg_o.media)
    except AttributeError:
        pass


@register(outgoing=True, pattern="^.filter (.*)")
async def add_new_filter(new_handler):
    """ For .filter command, allows adding new filters in a chat """
    try:
        if not (await handler.get_sender()).bot:
            if not is_mongo_alive() or not is_redis_alive():
                await handler.edit("`Database connections failing!`")
                return
    keyword = new_handler.pattern_match.group(1)
    msg = await new_handler.get_reply_message()
    if not msg:
        await new_handler.edit(
            "`I need something to save as reply to the filter.`")
    elif BOTLOG_CHATID:
        await new_handler.client.send_message(
            BOTLOG_CHATID, f"#FILTER\
        \nCHAT: {new_handler.chat.title}\
        \nTRIGGER: {keyword}\
        \nThe following message is saved as the filter's reply data for the chat, please do NOT delete it !!"
        )
        msg_o = await new_handler.client.forward_messages(
            entity=BOTLOG_CHATID,
            messages=msg,
            from_peer=new_handler.chat_id,
            silent=True)
    else:
        await new_handler.edit(
            "`This feature requires the BOTLOG_CHATID to be set.`")
        return
    success = "`Filter` **{}** `{} successfully`"
    if add_filter(str(new_handler.chat_id), keyword, msg_o.id) is True:
        await new_handler.edit(success.format(keyword, 'added'))
    else:
        await new_handler.edit(success.format(keyword, 'updated'))


@register(outgoing=True, pattern="^.stop (.*)")
async def remove_a_filter(r_handler):
    """ For .stop command, allows you to remove a filter from a chat. """
    try:
        if not (await handler.get_sender()).bot:
            if not is_mongo_alive() or not is_redis_alive():
                await handler.edit("`Database connections failing!`")
                return
    filt = r_handler.pattern_match.group(1)
    if not remove_filter(r_handler.chat_id, filt):
        await r_handler.edit("`Filter` **{}** `doesn't exist.`".format(filt))
    else:
        await r_handler.edit(
            "`Filter` **{}** `was deleted successfully`".format(filt))


@register(outgoing=True, pattern="^.rmbotfilters (.*)")
async def kick_marie_filter(event):
    """ For .rmfilters command, allows you to kick all \
        Marie(or her clones) filters from a chat. """
    cmd = event.text[0]
    bot_type = event.pattern_match.group(1).lower()
    if bot_type not in ["marie", "rose"]:
        await event.edit("`That bot is not yet supported!`")
        return
    await event.edit("```Will be kicking away all Filters!```")
    await sleep(3)
    resp = await event.get_reply_message()
    filters = resp.text.split("-")[1:]
    for i in filters:
        if bot_type.lower() == "marie":
            await event.reply("/stop %s" % (i.strip()))
        if bot_type.lower() == "rose":
            i = i.replace('`', '')
            await event.reply("/stop %s" % (i.strip()))
        await sleep(0.3)
    await event.respond(
        "```Successfully purged bots filters yaay!```\n Gimme cookies!")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "I cleaned all filters at " + str(event.chat_id))


@register(outgoing=True, pattern="^.filters$")
async def filters_active(event):
    """ For .filters command, lists all of the active filters in a chat. """
    try:
        if not (await handler.get_sender()).bot:
            if not is_mongo_alive() or not is_redis_alive():
                await handler.edit("`Database connections failing!`")
                return
    transact = "`There are no filters in this chat.`"
    filters = get_filters(event.chat_id)
    for filt in filters:
        if transact == "`There are no filters in this chat.`":
            transact = "Active filters in this chat:\n"
            transact += "`{}`\n".format(filt.keyword)
        else:
            transact += "`{}`\n".format(filt.keyword)

    await event.edit(transact)


CMD_HELP.update({
    "filter":
    ".filters\
    \nUsage: Lists all active userbot filters in a chat.\
    \n\n.filter <keyword>\
    \nUsage: Saves the replied message as a reply to the 'keyword'.\
    \nThe bot will reply to the message whenever 'keyword' is mentioned.\
    \nWorks with everything from files to stickers.\
    \n\n.stop <filter>\
    \nUsage: Stops the specified filter.\
    \n\n.rmbotfilters <marie/rose>\
    \nUsage: Removes all filters of admin bots (Currently supported: Marie, Rose and their clones.) in the chat."
})
