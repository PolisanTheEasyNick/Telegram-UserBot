from userbot.events import register
from userbot import MAC_ADDRESS as MAC
from userbot import BOTLOG, bot, BOTLOG_CHATID, CMD_HELP
from wakeonlan import send_magic_packet
@register(outgoing=True, pattern=r"^\.boot$")
async def boot(bt):
    if MAC is None:
      await bt.edit("**We don't support magic! No MAC ADDRESS!**")
      return
    send_magic_packet(MAC)
    await bt.edit("**Succesfully booted!**")
CMD_HELP.update({"boot": "Boot your PC on local server with MAC, given in conf file."})
