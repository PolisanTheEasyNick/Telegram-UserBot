from userbot import BOTLOG, bot, BOTLOG_CHATID, CMD_HELP, STEAMAPI, STEAMUSER, DEFAULT_BIO, OSU_USERID, OSU_CLIENT_ID, OSU_CLIENT_SECRET, OSU_REDIRECT_URL, OSU_SERVER_PORT
from userbot.events import register
from os import environ
import requests
from asyncio import sleep, gather, get_event_loop
from telethon import functions, types
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors.rpcerrorlist import FloodWaitError
from osu import Client
import socket
import threading
import time
from json import loads, JSONDecodeError
import userbot.modules.misc as miscModule

GAMECHECK = False
stockEmoji = None
currentEmoji = None
isPremium = False
isDefault = True
mustDisable = False
enableSteam = True
enableOsu = True
isPlaying = False
steamNeedToUpdate = False
steamUpdated = False
client = Client.from_client_credentials(OSU_CLIENT_ID, OSU_CLIENT_SECRET, OSU_REDIRECT_URL)

def osuServer():
  osuInfo = "none"
  host = "0.0.0.0"
  while not mustDisable and not miscModule.shutDown:
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, int(OSU_SERVER_PORT)))
        s.settimeout(2) #listening for 2 seconds for shutdown or restart case
        s.listen()
        conn, addr = s.accept()
        conn.settimeout(2)
        with conn:
          if mustDisable:
            conn.close()
            s.close()
            break
          try:
            data = conn.recv(1024)
            conn.sendall(bytes("received", "UTF-8"))
          except socket.timeout:
            conn.close()
            continue
          except socket.error as e:
            conn.close()
            s.close()
            time.sleep(5)
            continue
          if len(data) == 0:
            continue
          if data:
            if(osuInfo != data):
              osuInfo = data.decode("UTF-8")
              try:
                osuFile = open("osuTemp", "w")
                osuFile.write(osuInfo)
                osuFile.close()
              except Exception as e:
                break
      conn.close()
      s.close()
    except KeyboardInterrupt:
      s.close()
      break
    except Exception as e:
      s.close()
      time.sleep(5)

serverThread = threading.Thread(target=osuServer, name="Osu server for receiving info")

def steam_info():
  response = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAMAPI}&steamids={STEAMUSER}')
  return response.json()

def osu_info():
  if OSU_SERVER_PORT != "":
    osuFile = open("osuTemp", "r")
    osuInfo = osuFile.read()
    osuFile.close()
    if osuInfo == "none":
      return None
    try:
      osuJson = loads(osuInfo)
      return osuJson
    except JSONDecodeError:
      return None
    except Exception as e:
      pass #using site method
  return client.get_user(OSU_USERID).is_online

async def update_game_info():
  global GAMECHECK
  global isPremium
  global isDefault
  global stockEmoji
  global currentEmoji
  global mustDisable
  global enableOsu
  global enableSteam
  global isPlaying
  global steamNeedToUpdate
  global steamUpdated
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
  "20900": 5402292448539978864, #Witcher 1
  "20920": 5402508708733266023, #witcher 2
  "292030": 5247031932000149461, #witcher 3
  "400": 5328109481345690460, #portal 1
  "620": 5328109481345690460, #portal 2
  "2012840": 5328109481345690460, #portal rtx
  "1113560": 5274055672953054735, #nier replicant
  "524220": 5274055672953054735, #nier automata
  "244210": 5402495261190663483, #assetto corsa
  "1174180": 5400083783082845798, #RDR 2
  "275850": 5402372098708481565, #No Man's Sky
  "990080": 5402498941977634892, #Hogwarts Legacy
  "70": 5402386138956573252, #HL 1
  "220": 5402386138956573252, #HL 2
  "380": 5402386138956573252, #HL 2, EP 1
  "420": 5402386138956573252, #HL 2, EP 2
  "340": 5402386138956573252, #HL 2: Lost Coast
  "320": 5402386138956573252, #HL 2: Deathmatch
  "130": 5402386138956573252, #HL: Blue-Shift
  "360": 5402386138956573252, #HL Deathmatch: Source
  "50": 5402386138956573252, #HL: Opposing Force
  "280": 5402386138956573252, #HL: Source
  "322170": 5402191259110484152, #Geometry Dash
  "227300": 5402444434547679717, #ETS 2
  "1850570": 5402127916932801115, #DEATH STRANDING: DIRECTOR'S CUT
  "1190460": 5402127916932801115, #DEATH STRANDING
  "870780": 5402430304105275959, #Control
  "493490": 5402374224717291970, #City Car Driving
  "": 5244764300937011946 #default game icon
  }
  if mustDisable:
    GAMECHECK = False
    mustDisable = False
    if isDefault == False:
      if isPremium:
        try:
          if currentEmoji != stockEmoji:
            await bot(functions.account.UpdateEmojiStatusRequest(
              emoji_status=types.EmojiStatus(
               document_id=stockEmoji
                )
              ))
            currentEmoji = stockEmoji
        except FloodWaitError as e:
          if BOTLOG:
            await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds.")
          await sleep(e.seconds)
          if currentEmoji != stockEmoji:
            await bot(functions.account.UpdateEmojiStatusRequest(
              emoji_status=types.EmojiStatus(
               document_id=stockEmoji
                )
              ))
            currentEmoji = stockEmoji
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
          isPlaying = True
          #playing some steam game
          if gameID != oldGameID or steamNeedToUpdate:
            oldGameID = gameID
            if gameID in games:
              if isDefault or isPlayingOsu or isPlayingSteam == False or (steamNeedToUpdate and steamUpdated == False):
                if steamNeedToUpdate:
                  steamNeedToUpdate = False
                  steamUpdated = True
                isPlayingSteam = True
                if isPremium:
                  try:
                    if currentEmoji != games[gameID]:
                      await bot(functions.account.UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                         document_id=games[gameID]
                        )
                      ))
                      currentEmoji=games[gameID]
                  except FloodWaitError as e:
                    if BOTLOG:
                      await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                    await sleep(e.seconds)
                    if currentEmoji != games[gameID]:
                      await bot(functions.account.UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                         document_id=games[gameID]
                        )
                      ))
                      currentEmoji = games[gameID]
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
              if isDefault or isPlayingOsu or isPlayingSteam == False or (steamNeedToUpdate and steamUpdated == False):
                isPlayingSteam = True
                if steamNeedToUpdate:
                  steamNeedToUpdate = False
                  steamUpdated = True
                if isPremium:
                  try:
                    if currentEmoji != games[""]:
                      await bot(functions.account.UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                         document_id=games[""]
                        )
                      ))
                      currentEmoji = games[""]
                  except FloodWaitError as e:
                    if BOTLOG:
                      await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                    await sleep(e.seconds)
                    if currentEmoji != games[""]:
                      await bot(functions.account.UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                         document_id=games[""]
                        )
                      ))
                      currentEmoji = games[""]
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
                continue
        except:
          #nothing playing in steam
          isPlayingSteam = False
          if isDefault == False and isPlayingOsu == False:
            if isPremium:
              try:
                if currentEmoji != stockEmoji:
                  await bot(functions.account.UpdateEmojiStatusRequest(
                    emoji_status=types.EmojiStatus(
                      document_id=stockEmoji
                      )
                    ))
                  currentEmoji = stockEmoji
              except FloodWaitError as e:
                if BOTLOG:
                  await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                await sleep(e.seconds)
                if currentEmoji != stockEmoji:
                  await bot(functions.account.UpdateEmojiStatusRequest(
                    emoji_status=types.EmojiStatus(
                      document_id=stockEmoji
                      )
                    ))
                  currentEmoji=stockEmoji
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
        if isDefault or (isPlayingSteam == False and displayingOsu == False) or oldOsuStatus != osuinfo:
          try:
            artist = osuinfo[0]["artist"]
            title = osuinfo[0]["title"]
            BPM = osuinfo[0]["BPM"]
            SR = osuinfo[0]["SR"]
            STATUS = osuinfo[0]["STATUS"]
            oldOsuStatus = osuinfo
            if STATUS == 2:
              gameBio = f"🎮osu!: {artist} - {title} | 🥁: {BPM} | {SR}*"
            elif STATUS == 11:
              gameBio = f"🎮osu!: Searching for multiplayer lobby"
            elif STATUS == 12:
              gameBio = f"🎮osu!: Chilling in multiplayer lobby"
            else:
              gameBio = f"🎮osu!: Chilling in main menu"
          except Exception as e:
            if BOTLOG:
              bot.send_message(BOTLOG_CHATID, f"#GAMES\nOSU!: Exception {e} while trying to parse info from client")
            gameBio="🎮: Clicking circles!"
          try:
            await bot(UpdateProfileRequest(about=gameBio))
          except AboutTooLongError:
            try:
              gameBio = f"osu!: {artist} - {title}"
              await bot(UpdateProfileRequest(about=gameBio))
            except AboutTooLongError:
              maxSymbols = 70
              if me.premium:
                maxSymbols = 140
              toCut = maxSymbols-3
              gameBio = short_bio[:toCut]
              gameBio += '...'
              oldOsuStatus = gameBio
              await bot(UpdateProfileRequest(about=gameBio))
          except FloodWaitError as e:
            if BOTLOG:
              bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
            await sleep(e.seconds)
            await bot(UpdateProfileRequest(about=gameBio))
          if isPremium:
            try:
              if currentEmoji != games["osu"]:
                await bot(functions.account.UpdateEmojiStatusRequest(
                  emoji_status=types.EmojiStatus(
                    document_id=games["osu"]
                    )
                  ))
                currentEmoji = games["osu"]
            except FloodWaitError as e:
              if BOTLOG:
               await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
              await sleep(e.seconds)
              if currentEmoji != games["osu"]:
                await bot(functions.account.UpdateEmojiStatusRequest(
                  emoji_status=types.EmojiStatus(
                    document_id=games["osu"]
                    )
                  ))
                currentEmoji = games["osu"]
          isDefault = False
          isPlayingOsu = True
          displayingOsu = True
          steamUpdated = False
      else: #osu offline
        isPlayingOsu = False
        if isPlayingSteam:
          if steamUpdated == False:
            steamNeedToUpdate = True
          continue
        isPlaying = False
        if isDefault == False:
          if isPremium:
            try:
               if currentEmoji != stockEmoji:
                 await bot(functions.account.UpdateEmojiStatusRequest(
                  emoji_status=types.EmojiStatus(
                    document_id=stockEmoji
                    )
                  ))
               currentEmoji = stockEmoji
            except FloodWaitError as e:
              if BOTLOG:
                await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
              await sleep(e.seconds)
              if currentEmoji != stockEmoji:
                await bot(functions.account.UpdateEmojiStatusRequest(
                  emoji_status=types.EmojiStatus(
                    document_id=stockEmoji
                    )
                  ))
                currentEmoji = stockEmoji
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
  global currentEmoji
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
    await e.edit("`Game checker already enabled! Updating stock emoji...`")
    me = await bot.get_me()
    stockEmoji = me.emoji_status.document_id
    return
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
  stockEmoji = me.emoji_status.document_id
  isPremium = me.premium
  if GAMECHECK == False:
    await e.edit("`Game checker enabled!`")
    if BOTLOG:
      await bot.send_message(BOTLOG_CHATID, "#GAMES\nEnabled game checker")
    GAMECHECK = True
    serverThread = threading.Thread(target=osuServer, name="Osu server for receiving info")
    serverThread.start()
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
  global currentEmoji
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
      if currentEmoji != stockEmoji:
        await bot(functions.account.UpdateEmojiStatusRequest(
          emoji_status=types.EmojiStatus(
            document_id=stockEmoji
          )
        ))
        currentEmoji=stockEmoji
    except FloodWaitError as e:
      if BOTLOG:
       await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
      await sleep(e.seconds)
      if currentEmoji != stockEmoji:
        await bot(functions.account.UpdateEmojiStatusRequest(
          emoji_status=types.EmojiStatus(
            document_id=stockEmoji
          )
        ))
        currentEmoji = stockEmoji
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



