from userbot import bot, QUOTES_LIST_PATH, DEFAULT_BIO, BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import register
from random import choice


@register(outgoing=True, pattern=r"^\.getemoji$")
async def getEmoji(e):
  me = await bot.get_me()
  isPremium = me.premium
  if isPremium:
    await e.edit(f"**Current emoji ID at status:** `{me.emoji_status.document_id}`")
    return
  else:
    await e.edit(f"**You need Telegram Premium for accessing current emoji status ID**")

async def getStatus():
  if QUOTES_LIST_PATH:
    try:
      with open(QUOTES_LIST_PATH, 'r') as file:
        lines = file.readlines()
        return choice(lines).strip()
    except Exception as err:
      if BOTLOG:
        await bot.send_message(BOTLOG_CHATID, f"#STATUS: Can't get random status from file: {err}")
      return DEFAULT_BIO
  return DEFAULT_BIO


CMD_HELP.update({"status": ['Status',
    " - `.getemoji`: Get document id of current emoji at status.\n"]
})
