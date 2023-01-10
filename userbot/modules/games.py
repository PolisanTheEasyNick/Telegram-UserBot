from userbot import BOTLOG, bot, BOTLOG_CHATID, CMD_HELP, STEAMAPI, STEAMUSER, DEFAULT_BIO, OSU_USERID, OSU_CLIENT_ID, OSU_CLIENT_SECRET, OSU_REDIRECT_URL
from userbot.events import register
from os import environ
import requests
from asyncio import sleep, gather, get_event_loop
from telethon import functions, types
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors.rpcerrorlist import FloodWaitError
from osu import Client

GAMECHECK = False
stockEmoji = ""
isPremium = False
isDefault = True
mustDisable = False
enableSteam = True
enableOsu = True
isPlaying = False
client = Client.from_client_credentials(OSU_CLIENT_ID, OSU_CLIENT_SECRET, OSU_REDIRECT_URL)


def steam_info():
  response = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAMAPI}&steamids={STEAMUSER}')
  return response.json()

def osu_info():
  return client.get_user(OSU_USERID).is_online

async def update_game_info():
  global GAMECHECK
  global isPremium
  global isDefault
  global stockEmoji
  global mustDisable
  global enableOsu
  global enableSteam
  global isPlaying
  mustDisable = False
  gameID = ""
  gameName = ""
  oldGameID = ""
  oldOsuStatus = ""
  isPlayingSteam = False
  isPlayingOsu = False
  displayingOsu = False
  games = {
  "osu": 5238084986841607939,
  "977950": 5235672984747779211, #adofai
  "1091500": 5244454474881180648, #cyberpunk 2077
  "730": 5242547097084897042, #cs go
  "33230": 5242331923518332969, #AC2
  "41890": 5242331923518332969, #AC brotherhood
  "201870": 5242331923518332969, #AC revelations
  "911400": 5242331923518332969, #AC 3 remastered
  "289650": 5242331923518332969, #AC Unity
  "368500": 5242331923518332969, #AC Syndicate
  "812140": 5242331923518332969, #AC Odyssey
  "311560": 5242331923518332969, #AC Rogue
  "1245620": 5247083299809009542, #Elden Ring
  "20900": 5247031932000149461, #Witcher 1
  "20920": 5247031932000149461, #witcher 2
  "292030": 5247031932000149461, #witcher 3
  "400": 5328109481345690460, #portal 1
  "620": 5328109481345690460, #portal 2
  "2012840": 5328109481345690460, #portal rtx
  "1113560": 5274055672953054735, #nier replicant
  "524220": 5274055672953054735, #nier automata
  "": 5244764300937011946 #default game icon
  }
  if mustDisable:
    GAMECHECK = False
    mustDisable = False
    if isDefault == False:
      if isPremium:
        try:
          await bot(functions.account.UpdateEmojiStatusRequest(
            emoji_status=types.EmojiStatus(
             document_id=stockEmoji
              )
            ))
        except FloodWaitError as e:
          if BOTLOG:
            await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds.")
          await sleep(e.seconds)
          await bot(functions.account.UpdateEmojiStatusRequest(
            emoji_status=types.EmojiStatus(
             document_id=stockEmoji
              )
            ))
      try:
        await bot(UpdateProfileRequest(about=DEFAULT_BIO))
      except FloodWaitError as e:
        if BOTLOG:
          await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
        await sleep(e.seconds)
        await bot(UpdateProfileRequest(about=DEFAULT_BIO))
      isDefault = True

  while GAMECHECK:
    if isDefault:
      oldGameID = 0
      oldOsuStatus = ""
      me = await bot.get_me()
      stockEmoji = me.emoji_status.document_id
    while True:
      try:
        if enableSteam:
          steaminfo = steam_info()
        if enableOsu:
          osuinfo = osu_info()
      except Exception as e:
        if BOTLOG:
          await bot.send_message(BOTLOG_CHATID, f"#GAMES: Catched exception:\n{e}.\nWaiting 5 sec and trying again")
        await sleep(5)
        continue
      break
    try:
      if steaminfo:
        await sleep(1)
        try:
          gameID = steaminfo['response']['players'][0]['gameid']
          gameName = steaminfo['response']['players'][0]['gameextrainfo']
          isPlayingSteam = True
          isPlaying = True
          #playing some steam game
          if gameID != oldGameID:
            oldGameID = gameID
            if gameID in games:
              if isDefault or isPlayingOsu or isPlayingSteam == False:
                isPlayingSteam == True
                if isPremium:
                  try:
                    await bot(functions.account.UpdateEmojiStatusRequest(
                      emoji_status=types.EmojiStatus(
                       document_id=games[gameID]
                      )
                    ))
                  except FloodWaitError as e:
                    if BOTLOG:
                      await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                    await sleep(e.seconds)
                    await bot(functions.account.UpdateEmojiStatusRequest(
                      emoji_status=types.EmojiStatus(
                       document_id=games[gameID]
                      )
                    ))
                gameBio="🎮: " + gameName
                try:
                  await bot(UpdateProfileRequest(about=gameBio))
                except FloodWaitError as e:
                  if BOTLOG:
                    await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                  await sleep(e.seconds)
                  await bot(UpdateProfileRequest(about=gameBio))
                isDefault = False
                displayingOsu = False
            else: #custom game
              if isDefault or isPlayingOsu or isPlayingSteam == False:
                if isPremium:
                  try:
                    await bot(functions.account.UpdateEmojiStatusRequest(
                      emoji_status=types.EmojiStatus(
                       document_id=games[""]
                      )
                    ))
                  except FloodWaitError as e:
                    if BOTLOG:
                      await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                    await sleep(e.seconds)
                    await bot(functions.account.UpdateEmojiStatusRequest(
                      emoji_status=types.EmojiStatus(
                       document_id=games[""]
                      )
                    ))
                gameBio="🎮: " + gameName
                try:
                  await bot(UpdateProfileRequest(about=gameBio))
                except FloodWaitError as e:
                  if BOTLOG:
                    await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                  await sleep(e.seconds)
                  await bot(UpdateProfileRequest(about=gameBio))
                isDefault = False
                isPlayingSteam = True
                displayingOsu = False
        except:
          #nothing playing in steam
          isPlayingSteam = False
          if isDefault == False and isPlayingOsu == False:
            if isPremium:
              try:
                await bot(functions.account.UpdateEmojiStatusRequest(
                  emoji_status=types.EmojiStatus(
                    document_id=stockEmoji
                    )
                  ))
              except FloodWaitError as e:
                if BOTLOG:
                  await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                await sleep(e.seconds)
                await bot(functions.account.UpdateEmojiStatusRequest(
                  emoji_status=types.EmojiStatus(
                    document_id=stockEmoji
                    )
                  ))
            try:
              await bot(UpdateProfileRequest(about=DEFAULT_BIO))
            except FloodWaitError as e:
              if BOTLOG:
                await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
              await sleep(e.seconds)
              await bot(UpdateProfileRequest(about=DEFAULT_BIO))
            isDefault = True
          isPlayingSteam = False
      if osuinfo:
        #playing osu
        isPlaying = True
        isPlayingOsu = True
        if isDefault or (isPlayingSteam == False and displayingOsu == False):
          me = await bot.get_me()
          stockEmoji = me.emoji_status.document_id
          gameBio="🎮: Clicking circles!"
          try:
            await bot(UpdateProfileRequest(about=gameBio))
          except FloodWaitError as e:
            if BOTLOG:
              bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
            await sleep(e.seconds)
            await bot(UpdateProfileRequest(about=gameBio))
          if isPremium:
            try:
              await bot(functions.account.UpdateEmojiStatusRequest(
                emoji_status=types.EmojiStatus(
                  document_id=games["osu"]
                  )
                ))
            except FloodWaitError as e:
              if BOTLOG:
               await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
              await sleep(e.seconds)
              await bot(functions.account.UpdateEmojiStatusRequest(
                emoji_status=types.EmojiStatus(
                  document_id=games["osu"]
                  )
                ))
          isDefault = False
          isPlayingOsu = True
          displayingOsu = True
      else: #osu offline
        isPlayingOsu = False
        if isPlayingSteam:
          continue
        isPlaying = False
        if isDefault == False:
          if isPremium:
            try:
               await bot(functions.account.UpdateEmojiStatusRequest(
                emoji_status=types.EmojiStatus(
                  document_id=stockEmoji
                  )
                ))
            except FloodWaitError as e:
              if BOTLOG:
                await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
              await sleep(e.seconds)
              await bot(functions.account.UpdateEmojiStatusRequest(
                emoji_status=types.EmojiStatus(
                  document_id=stockEmoji
                  )
                ))
          try:
            await bot(UpdateProfileRequest(about=DEFAULT_BIO))
          except FloodWaitError as e:
            if BOTLOG:
              await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
            await sleep(e.seconds)
            await bot(UpdateProfileRequest(about=DEFAULT_BIO))
          isDefault = True
          displayingOsu = False
        isPlayingOsu = False
        await sleep(10)
    except Exception as e:
      if BOTLOG:
        await bot.send_message(BOTLOG_CHATID, f"#GAMES: Catched exception:\n{e}.\nWaiting 5 sec and trying again")
      await sleep(5)

@register(outgoing=True, pattern=r"^\.gameon$")
async def games(e):
  global stockEmoji
  global isDefault
  global isPremium
  global GAMECHECK
  global enableSteam
  global enableOsu
  global mustDisable
  enableSteam = True
  enableOsu = True
  if environ.get("isSuspended") == "True":
    return
  if GAMECHECK:
    await e.edit("`Game checker already enabled!`")
  if STEAMAPI == '0' or STEAMUSER == '0':
    e.edit("**Check STEAM_API and STEAM_USERID, module started without Steam checking**")
    enableSteam = False
    return
  if OSU_USERID == '0' or OSU_CLIENT_ID == '0' or OSU_CLIENT_SECRET == '0' or OSU_REDIRECT_URL == '0':
    e.edit("**Check OSU_USERID, OSU_CLIENT_ID, OSU_CLIENT_SECRET and OSU_REDIRECT_URL. Module started without osu! checking**")
    enableOsu = False
    return
  if BOTLOG:
      if enableSteam == False:
        await bot.send_message(BOTLOG_CHATID, "#GAMES\nCheck STEAM_API and STEAM_USERID")
      if enableOsu == False:
        await bot.send_message(BOTLOG_CHATID, "#GAMES\nCheck OSU_USERID, OSU_CLIENT_ID, OSU_CLIENT_SECRET and OSU_REDIRECT_URL")
  if enableSteam == False and enableOsu == False:
    e.edit("**Can't continue, check config.env and botlog**")
    return
  me = await bot.get_me()
  isPremium = me.premium
  #5235672984747779211 - adofai
  #5238084986841607939 - osu!
  if GAMECHECK == False:
    await e.edit("`Game checker enabled!`")
    if BOTLOG:
      await bot.send_message(BOTLOG_CHATID, "#GAMES\nEnabled game checker")
    GAMECHECK = True
    await update_game_info()
  
@register(outgoing=True, pattern=r"^\.gameoff$")
async def gamesoff(e):
  if environ.get("isSuspended") == "True":
    return
  global GAMECHECK
  global OSUCHECK
  global mustDisable
  global isPremium
  global stockEmoji
  GAMECHECK = False
  mustDisable = True
  try:
    await bot(UpdateProfileRequest(about=DEFAULT_BIO))
  except FloodWaitError as e:
    if BOTLOG:
      await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
    await sleep(e.seconds)
    await bot(UpdateProfileRequest(about=DEFAULT_BIO))
  if isPremium:
    try:
      await bot(functions.account.UpdateEmojiStatusRequest(
        emoji_status=types.EmojiStatus(
          document_id=stockEmoji
        )
      ))
    except FloodWaitError as e:
      if BOTLOG:
       await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
      await sleep(e.seconds)
      await bot(functions.account.UpdateEmojiStatusRequest(
        emoji_status=types.EmojiStatus(
          document_id=stockEmoji
        )
      ))
    try:
      await bot(UpdateProfileRequest(about=DEFAULT_BIO))
    except FloodWaitError as e:
      if BOTLOG:
       await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
      await sleep(e.seconds)
      await bot(UpdateProfileRequest(about=DEFAULT_BIO))
  await e.edit("`Games checker disabled!`")
  if BOTLOG:
    await bot.send_message(BOTLOG_CHATID, '#GAMES\nDisabled games checker')


@register(outgoing=True, pattern=r"^\.getemoji$")
async def getEmoji(e):
  me = await bot.get_me()
  isPremium = me.premium
  if isPremium:
    await e.edit(f"**Current emoji at status ID:** `{me.emoji_status.document_id}`")
    return
  else:
    await e.edit(f"**You need Telegram Premium for accessing current emoji status ID**")

CMD_HELP.update({"games": ['Games',
    " - `.gameon`: Enable games bio and emoji updating.\n"
    " - `.gameoff`: Disable games bio and emoji updating.\n"
    " - `.getemoji`: Get ID of current status emoji.\n"
    ]
})


