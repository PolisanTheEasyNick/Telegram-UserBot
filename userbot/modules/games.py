from userbot import BOTLOG, bot, BOTLOG_CHATID, CMD_HELP, STEAMAPI, STEAMUSER, DEFAULT_BIO, OSU_USERID, OSU_CLIENT_ID, OSU_CLIENT_SECRET, OSU_REDIRECT_URL, OSU_SERVER_PORT, STEAM_PROFILE_LINK
from userbot.events import register
from os import environ
import requests
from bs4 import BeautifulSoup
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

games_emoji_list = {
    "osu": (5238084986841607939,),
    "977950": ("A Dance of Fire and Ice", 5235672984747779211),
    "1091500": ("Cyberpunk 2077", 5244454474881180648),
    "730": ("Counter-Strike: Global Offensive", 5242547097084897042),
    "33230": ("Assassin's Creed II", 5242331923518332969),
    "48190": ("Assassin's Creed Brotherhood", 5242331923518332969),
    "201870": ("Assassin's Creed Revelations", 5242331923518332969),
    "911400": ("Assassin's Creed III Remastered", 5242331923518332969),
    "289650": ("Assassin's Creed Unity", 5242331923518332969),
    "368500": ("Assassin's Creed Syndicate", 5242331923518332969),
    "812140": ("Assassin's Creed Odyssey", 5242331923518332969),
    "311560": ("Assassin's Creed Rogue", 5242331923518332969),
    "1245620": ("ELDEN RING", 5247083299809009542),
    "20900": ("The Witcher: Enhanced Edition", 5402292448539978864),
    "20920": ("The Witcher 2: Assassins of Kings Enhanced Edition", 5402508708733266023),
    "292030": ("The Witcher 3: Wild Hunt", 5247031932000149461),
    "400": ("Portal", 5328109481345690460),
    "620": ("Portal 2", 5328109481345690460),
    "2012840": ("Portal with RTX", 5328109481345690460),
    "1113560": ("NieR Replicant ver.1.22474487139...", 5274055672953054735),
    "524220": ("NieR: Automata", 5274055672953054735),
    "244210": ("Assetto Corsa", 5402495261190663483),
    "1174180": ("Red Dead Redemption 2", 5400083783082845798),
    "275850": ("No Man's Sky", 5402372098708481565),
    "990080": ("Hogwarts Legacy", 5402498941977634892),
    "70": ("Half-Life", 5402386138956573252),
    "220": ("Half-Life 2", 5402386138956573252),
    "380": ("Half-Life 2: Episode One", 5402386138956573252),
    "420": ("Half-Life 2: Episode Two", 5402386138956573252),
    "340": ("Half-Life 2: Lost Coast", 5402386138956573252),
    "320": ("Half-Life 2: Deathmatch", 5402386138956573252),
    "130": ("Half-Life: Blue Shift", 5402386138956573252),
    "360": ("Half-Life Deathmatch: Source", 5402386138956573252),
    "50": ("Half-Life: Opposing Force", 5402386138956573252),
    "280": ("Half-Life: Source", 5402386138956573252),
    "322170": ("Geometry Dash", 5402191259110484152),
    "227300": ("Euro Truck Simulator 2", 5402444434547679717),
    "1850570": ("DEATH STRANDING DIRECTOR'S CUT", 5402127916932801115),
    "1190460": ("DEATH STRANDING", 5402127916932801115),
    "870780": ("Control Ultimate Edition", 5402430304105275959),
    "493490": ("City Car Driving", 5402374224717291970),
    "": ("default game icon", 5244764300937011946)
}

#if passed game name -> returns game steam id
#if passed game steam id -> return emoji id
def get_game(key):
    for game_id, game_info in games_emoji_list.items():
      if game_info[0] == key:
        return game_id
      elif game_id == key:
        return game_info[-1]
    return None

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
  if response:
    return response.json()
  response = requests.get(STEAM_PROFILE_LINK)
  soup = BeautifulSoup(response.text, 'html.parser')
  element = soup.find(class_="profile_in_game_header")
  text = ""
  if element:
    text = element.get_text()
  if text == "Currently Offline":
    return None
  elif text == "Currently Online":
    return None
  elif text == "Currently In-Game":
    game_name = soup.find(class_="profile_in_game_name").get_text()
    game_id = get_game(game_name)
    steam_info = {
      "response": {
        "players": [
            {
              "gameid": game_id,
              "gameextrainfo": game_name
            }
          ]
      }
    }
    return steam_info
  else:
    return None
    

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
        if enableSteam and not isPlayingOsu:
          steaminfo = steam_info()
        if enableOsu:
          osuinfo = osu_info()
      except Exception as e:
        if BOTLOG:
          await bot.send_message(BOTLOG_CHATID, f"#GAMES: Catched exception while trying to get info about games:\n{e}.\nWaiting 5 sec and trying again")
        await sleep(5)
        continue
      break
    try:
      if enableSteam and not isPlayingOsu:
        await sleep(1)
        try:
          gameID = steaminfo['response']['players'][0]['gameid']
          gameName = steaminfo['response']['players'][0]['gameextrainfo']
          isPlaying = True
          #playing some steam game
          if gameID != oldGameID or steamNeedToUpdate:
            oldGameID = gameID
            if gameID in games_emoji_list:
              if isDefault or isPlayingOsu or isPlayingSteam == False or (steamNeedToUpdate and steamUpdated == False):
                if steamNeedToUpdate:
                  steamNeedToUpdate = False
                  steamUpdated = True
                isPlayingSteam = True
                if isPremium:
                  try:
                    if currentEmoji != get_game(gameID):
                      await bot(functions.account.UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                         document_id=get_game(gameID)
                        )
                      ))
                      currentEmoji=get_game(gameID)
                  except FloodWaitError as e:
                    if BOTLOG:
                      await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                    await sleep(e.seconds)
                    if currentEmoji != get_game(gameID):
                      await bot(functions.account.UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                         document_id=get_game(gameID)
                        )
                      ))
                      currentEmoji = get_game(gameID)
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
                    if currentEmoji != get_game(""):
                      await bot(functions.account.UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                         document_id=get_game("")
                        )
                      ))
                      currentEmoji = get_game("")
                  except FloodWaitError as e:
                    if BOTLOG:
                      await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
                    await sleep(e.seconds)
                    if currentEmoji != get_game(""):
                      await bot(functions.account.UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                         document_id=get_game("")
                        )
                      ))
                      currentEmoji = get_game("")
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
          await sleep(30)
          continue
        except Exception as e:
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
      if enableOsu and osuinfo:
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
              if currentEmoji != get_game("osu"):
                await bot(functions.account.UpdateEmojiStatusRequest(
                  emoji_status = types.EmojiStatus(
                    document_id = get_game("osu")
                    )
                  ))
                currentEmoji = get_game("osu")
            except FloodWaitError as e:
              if BOTLOG:
               await bot.send_message(BOTLOG_CHATID, f"#GAMES\nFloodWaitError: waiting {e.seconds} seconds")
              await sleep(e.seconds)
              if currentEmoji != get_game("osu"):
                await bot(functions.account.UpdateEmojiStatusRequest(
                  emoji_status = types.EmojiStatus(
                    document_id = get_game("osu")
                    )
                  ))
                currentEmoji = get_game("osu")
          isDefault = False
          isPlayingOsu = True
          displayingOsu = True
          steamUpdated = False
        await sleep(1)
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
async def gameon(e):
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
  if (STEAMAPI == '0' or STEAMUSER == '0') and STEAM_PROFILE_LINK == "":
    await e.edit("**Check STEAM_API and STEAM_USERID or STEAM_PROFILE_LINK, module started without Steam checking**")
    enableSteam = False
  if OSU_USERID == '0' or OSU_CLIENT_ID == '0' or OSU_CLIENT_SECRET == '0' or OSU_REDIRECT_URL == '0':
    await e.edit("**Check OSU_USERID, OSU_CLIENT_ID, OSU_CLIENT_SECRET and OSU_REDIRECT_URL. Module started without osu! checking**")
    enableOsu = False
  if BOTLOG:
      if enableSteam == False:
        await bot.send_message(BOTLOG_CHATID, "#GAMES\nCheck STEAM_API and STEAM_USERID or STEAM_PROFILE_LINK")
      if enableOsu == False:
        await bot.send_message(BOTLOG_CHATID, "#GAMES\nCheck OSU_USERID, OSU_CLIENT_ID, OSU_CLIENT_SECRET and OSU_REDIRECT_URL")
  if enableSteam == False and enableOsu == False:
    await e.edit("**Can't continue, check config.env and botlog**")
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
async def gameoff(e):
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

CMD_HELP.update({"Games": ['games',
    " - `.gameon`: Enable games bio and emoji updating.\n"
    " - `.gameoff`: Disable games bio and emoji updating.\n"
    " - `.getemoji`: Get ID of current status emoji.\n"
    ]
})



