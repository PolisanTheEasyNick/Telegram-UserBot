from userbot import BOTLOG, bot, BOTLOG_CHATID, CMD_HELP, STEAMAPI, STEAMUSER, DEFAULT_BIO, OSU_USERID
from userbot.events import register
from os import environ
import requests
from asyncio import sleep, gather, get_event_loop
from telethon import functions, types
from telethon.tl.functions.account import UpdateProfileRequest
from requests_html import AsyncHTMLSession

GAMECHECK = False
stockEmoji = ""
isPremium = False
isDefault = True
mustDisable = False
enableSteam = True
enableOsu = True
isPlaying = False
session = AsyncHTMLSession()

def steam_info():
  response = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAMAPI}&steamids={STEAMUSER}')
  return response.json()

async def osu_info():
  r = await session.get(f'https://osu.ppy.sh/users/{OSU_USERID}')
  print("osu_info: rendering")
  await r.html.arender()
  print("osu_info: end render")
  online_status = r.html.find("div.profile-links__item")[1].text
  print(f"returning online_status: {online_status}")
  return online_status

async def update_game_info():
  global GAMECHECK
  global isPlaying
  global isPremium
  global isDefault
  global stockEmoji
  global mustDisable
  global enableOsu
  global enableSteam
  mustDisable = False
  gameID = ""
  gameName = ""
  oldGameID = ""
  oldOsuStatus = ""
  isPlaying = False
  games = {
  "osu": "5238084986841607939",
  "977950": "5235672984747779211", #adofai
  "": "5467583879948803288" #default game icon
  }
  if mustDisable:
    GAMECHECK = False
    mustDisable = False
    if isDefault == False:
      if isPremium:
        await bot(functions.account.UpdateEmojiStatusRequest(
          emoji_status=types.EmojiStatus(
            document_id=stockEmoji
            )
          ))
      await bot(UpdateProfileRequest(about=DEFAULT_BIO))
      isDefault = True

  while GAMECHECK:
    if isDefault == True:
      me = await bot.get_me()
      stockEmoji = me.emoji_status.document_id
      oldGameID = 0
      oldOsuStatus = ""
    while True:
      try:
        if enableSteam:
          steaminfo = steam_info()
        if enableOsu:
          osuinfo = await osu_info()
      except Exception as e:
        if BOTLOG:
          await bot.send_message(BOTLOG_CHATID, f"#GAMES: Catched exception:\n{e}.\nWaiting 5 sec and trying again")
        await sleep(5)
        continue
      break
    if steaminfo or osuinfo:
      try:
        await sleep(1)
        try:
          gameID = steaminfo['response']['players'][0]['gameid']
          gameName = steaminfo['response']['players'][0]['gameextrainfo']
          isPlaying = True
          isPlayingSteam = True
        except Exception as e:
          #nothing playing in steam
          isPlaying = False
          isPlayingSteam = False
          if "online" in osuinfo:
            if isDefault:
              me = await bot.get_me()
              stockEmoji = me.emoji_status.document_id
              isDefault = False
            isPlaying = True
            if isPremium:
              await bot(functions.account.UpdateEmojiStatusRequest(
                emoji_status=types.EmojiStatus(
                  document_id=5238084986841607939
                  )
                ))
            gameBio="🎮: Clicking circles!"
            await bot(UpdateProfileRequest(about=gameBio))
          else:
            print("osu: offline")
            isPlaying = False
            if isDefault == False:
              if isPremium:
                await bot(functions.account.UpdateEmojiStatusRequest(
                  emoji_status=types.EmojiStatus(
                    document_id=stockEmoji
                    )
                  ))
            await bot(UpdateProfileRequest(about=DEFAULT_BIO))
            isDefault = True
            await sleep(10)
            continue
        finally:
          if isPlayingSteam:
            #playing some steam game
            isPlaying = True
            print(f"steam: gameID: {gameID}, old: {oldGameID}")
            isDefault = False
            if gameID != oldGameID:
              oldGameID = gameID
              if gameID in games:
                if isPremium:
                  #set emoji to 5235672984747779211
                  print(f"steam: set game {gameID}")
                  await bot(functions.account.UpdateEmojiStatusRequest(
                    emoji_status=types.EmojiStatus(
                     document_id=games[gameID]
                    )
                  ))
                gameBio="🎮: " + gameName
                print(f"steam: setting bio: {gameBio}")
                await bot(UpdateProfileRequest(about=gameBio))
              else: #custom game
                print(f"steam: set gaming, game: {gameName}")
                if isPremium:
                  await bot(functions.account.UpdateEmojiStatusRequest(
                    emoji_status=types.EmojiStatus(
                     document_id=5467583879948803288
                    )
                  ))
                gameBio="🎮: " + gameName
                await bot(UpdateProfileRequest(about=gameBio))
      except Exception as e:
        if BOTLOG:
          await bot.send_message(BOTLOG_CHATID, f"#GAMES: Catched exception:\n{e}.\nWaiting 5 sec and trying again")
        await sleep(5)

@register(outgoing=True, pattern=r"^\.gameon$")
async def games(e):
  global stockEmoji
  global isPremium
  global GAMECHECK
  global enableSteam
  global enableOsu
  global mustDisable
  enableSteam = True
  enableOsu = True
  if environ.get("isSuspended") == "True":
    return
  if STEAMAPI == '0' or STEAMUSER == '0':
    e.edit("**Check STEAM_API and STEAM_USERID, module started**")
    enableSteam = False
    return
  if OSU_USERID == '0':
    e.edit("**Check OSU_USERID, module started**")
    enableOsu = False
    return
  if BOTLOG:
      if enableSteam == False:
        await bot.send_message(BOTLOG_CHATID, "#GAMES\nCheck STEAM_API and STEAM_USERID")
      if enableOsu == False:
        await bot.send_message(BOTLOG_CHATID, "#GAMES\nCheck OSU_USERID")
  if enableSteam == False and enableOsu == False:
    e.edit("**Can't continue, check botlog**")
    return
  me = await bot.get_me()
  isPremium = me.premium
  #5235672984747779211 - adofai
  #5238084986841607939 - osu!
  if GAMECHECK == False:
    await e.edit("`Game checker enabled!`")
    #gather(steam_info(), osu_info())
    GAMECHECK = True
    await update_game_info()
  
@register(outgoing=True, pattern=r"^\.gameoff$")
async def gamesoff(e):
  if environ.get("isSuspended") == "True":
    return
  global GAMECHECK
  global OSUCHECK
  global mustDisable
  global mustDisable
  global isPremium
  global stockEmoji
  GAMECHECK = False
  mustDisable = True
  await bot(UpdateProfileRequest(about=DEFAULT_BIO))
  if isPremium:
    await bot(functions.account.UpdateEmojiStatusRequest(
      emoji_status=types.EmojiStatus(
        document_id=stockEmoji
      )
    ))
    await bot(UpdateProfileRequest(about=DEFAULT_BIO))
  await e.edit("`Games checker disabled!`")
  if BOTLOG:
    await bot.send_message(BOTLOG_CHATID, '#GAMES\nDisabled games checker')

CMD_HELP.update({"games": ['Games',
    " - `.gameon`: Enable games bio and emoji updating.\n"
    " - `.gameoff`: Disable games bio and emoji updating.\n"
    ]
})
