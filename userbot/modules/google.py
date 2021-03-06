from search_engine_parser import GoogleSearch

from userbot import CMD_HELP
from userbot import BOTLOG, BOTLOG_CHATID
from userbot.events import register
from userbot.utils import parse_arguments
from os import environ

@register(outgoing=True, pattern=r"^\.google(?: |$)(.*)")
async def gsearch(q_event):
    """ For .google command, do a Google search. """
    if environ.get("isSuspended") == "True":
        return
    reply_message = await q_event.get_reply_message()
    query = q_event.pattern_match.group(1)
    opts, query = parse_arguments(query, ['page', 'limit'])

    page = opts.get('page', 1)
    gsearch = GoogleSearch()

    query = query or reply_message.text
    gresults = gsearch.search(query, 1)

    msg = ""
    limit = opts.get('limit', 5)
    for i in range(limit):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"[{title}]({link}) \n"
            msg += f"`{desc}`\n\n"
        except IndexError:
            break
    await q_event.edit("**Search Query:**\n`" + query + "`\n\n**Results:**\n" +
                       msg,
                       link_preview=False)
    if BOTLOG:
        await q_event.client.send_message(
            BOTLOG_CHATID,
            "Google Search query `" + query + "` was executed successfully",
        )

CMD_HELP.update({"google": ['Google',
    " - `.page`: Page of results to return.\n"
    " - `.limit`: Limit the number of returned results (defaults to 5).\n"]
})
