# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot initialization. """

import os
from distutils.util import strtobool as sb
from logging import DEBUG, INFO, basicConfig, getLogger
from sys import version_info

from dotenv import load_dotenv
from pyDownload import Downloader
from pylast import LastFMNetwork, md5
from pymongo import MongoClient
from redis import StrictRedis
from requests import get
from telethon import TelegramClient
from telethon.sessions import StringSession
#from google.cloud import texttospeech_v1 as tts
#from google.cloud import speech_v1 as stt

load_dotenv("config.env")

# Bot Logs setup:
CONSOLE_LOGGER_VERBOSE = sb(os.environ.get("CONSOLE_LOGGER_VERBOSE", "False"))

if CONSOLE_LOGGER_VERBOSE:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=DEBUG,
    )
else:
    basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                level=INFO)
LOGS = getLogger(__name__)

if version_info[0] < 3 or version_info[1] < 6:
    LOGS.error("You MUST have a python version of at least 3.6."
               " Multiple features depend on this. Bot quitting.")
    quit(1)

# Check if the config was edited by using the already used variable
CONFIG_CHECK = os.environ.get(
    "___________PLOX_______REMOVE_____THIS_____LINE__________", None)

if CONFIG_CHECK:
    LOGS.error("Please remove the line mentioned in the first \
         hashtag from the config.env file")
    quit(1)
    
# OCR API key
OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY", None)

# remove.bg API key
REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY", None)

API_KEY = os.environ.get("API_KEY", None)

API_HASH = os.environ.get("API_HASH", None)

KUTT_IT_API_KEY = os.environ.get("KUTT_IT_API_KEY", None)

BOTLOG = sb(os.environ.get("BOTLOG", "False"))

BOTLOG_CHATID = int(os.environ.get("BOTLOG_CHATID")) if BOTLOG else 0

PM_AUTO_BAN = sb(os.environ.get("PM_AUTO_BAN", "False"))

MONGO_DB_URI = os.environ.get("MONGO_DB_URI", None)

SCREENSHOT_LAYER_ACCESS_KEY = os.environ.get("SCREENSHOT_LAYER_ACCESS_KEY",
                                             None)

OPEN_WEATHER_MAP_APPID = os.environ.get("OPEN_WEATHER_MAP_APPID", None)

WELCOME_MUTE = sb(os.environ.get("WELCOME_MUTE", "False"))

# Default .alive name
ALIVE_NAME = os.environ.get("ALIVE_NAME", None)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", None)



BIO_PREFIX = os.environ.get("BIO_PREFIX", None)
DEFAULT_BIO = os.environ.get("DEFAULT_BIO", None)

LASTFM_API = os.environ.get("LASTFM_API", None)
LASTFM_SECRET = os.environ.get("LASTFM_SECRET", None)
LASTFM_USERNAME = os.environ.get("LASTFM_USERNAME", None)
LASTFM_PASSWORD_PLAIN = os.environ.get("LASTFM_PASSWORD", None)
LASTFM_PASS = md5(LASTFM_PASSWORD_PLAIN)
if not LASTFM_USERNAME == "None":
    lastfm = LastFMNetwork(api_key=LASTFM_API,
                           api_secret=LASTFM_SECRET,
                           username=LASTFM_USERNAME,
                           password_hash=LASTFM_PASS)
else:
    lastfm = None

CURRENCY_API = os.environ.get("CURRENCY_API", None)

GDRIVE_FOLDER = os.environ.get("GDRIVE_FOLDER", None)
GENIUS_API = os.environ.get("GENIUS_API", None)

TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TMP_DOWNLOAD_DIRECTORY",
                                         "./downloads")
#audiotag.info
AUDIOTAG_API = os.environ.get("AUDIOTAG_API", None)

MAC_ADDRESS = os.environ.get("MAC", None)
IP_ADDRESS = os.environ.get("IP_ADDRESS", None)
# https://www.convertapi.com/
CONVERT_TOKEN = os.environ.get("CONVERT_API", None)

# wolframalpha.com
WOLFRAM_ID= os.environ.get("WOLFRAM_ID", None)

# background sound for voice messages
BG_DEFAULT= os.environ.get("BG_DEFAULT", 'r')

STRING_SESSION = os.environ.get("STRING_SESSION") or None #means heroku

STEAMAPI=os.environ.get("STEAM_API", '0')
STEAMUSER=os.environ.get("STEAM_USERID", '0')

OSU_USERID=os.environ.get("OSU_USERID", '0')
OSU_CLIENT_ID=os.environ.get("OSU_CLIENT_ID", '0')
OSU_CLIENT_SECRET=os.environ.get("OSU_CLIENT_SECRET", '0')
OSU_REDIRECT_URL=os.environ.get("OSU_REDIRECT_URL", '0')
OSU_SERVER_PORT=os.environ.get("OSU_SERVER_PORT", '0')

if STRING_SESSION:
    bot = TelegramClient(StringSession(STRING_SESSION), API_KEY, API_HASH)
else:
    bot = TelegramClient("userbot", API_KEY, API_HASH)

async def check_botlog_chatid():
    if not BOTLOG:
        return

    entity = await bot.get_entity(BOTLOG_CHATID)
    if entity.default_banned_rights.send_messages:
        LOGS.error(
            "Your account doesn't have rights to send messages to BOTLOG_CHATID "
            "group. Check if you typed the Chat ID correctly.")
        quit(1)


with bot:
    try:
        bot.loop.run_until_complete(check_botlog_chatid())
    except:
        LOGS.error("BOTLOG_CHATID environment variable isn't a "
                   "valid entity. Check your config.env file.")
        quit(1)

# Init Mongo
MONGOCLIENT = MongoClient(MONGO_DB_URI, 27017, serverSelectionTimeoutMS=1)
MONGO = MONGOCLIENT.userbot


def is_mongo_alive():
    try:
        MONGOCLIENT.server_info()
    except BaseException:
        return False
    return True


# Init Redis
# Redis will be hosted inside the docker container that hosts the bot
# We need redis for just caching, so we just leave it to non-persistent
REDIS = StrictRedis(host='localhost', port=6379, db=0)


def is_redis_alive():
    try:
        REDIS.ping()
        return True
    except BaseException:
        return False


# Download binaries for gen_direct_links module, give correct perms
if not os.path.exists('bin'):
    os.mkdir('bin')

url1 = 'https://raw.githubusercontent.com/yshalsager/megadown/master/megadown'
url2 = 'https://raw.githubusercontent.com/yshalsager/cmrudl.py/master/cmrudl.py'

dl1 = Downloader(url=url1, filename="bin/megadown")
dl1 = Downloader(url=url1, filename="bin/cmrudl")

os.chmod('bin/megadown', 0o755)
os.chmod('bin/cmrudl', 0o755)
"""
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None)
if GOOGLE_APPLICATION_CREDENTIALS:
    TTSClient = tts.TextToSpeechClient()
    STTClient = stt.SpeechClient()
else:
    TTSClient = None
    STTClient = None
"""
# Global Variables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
ISAFK = False
LASTMSG = {}
ENABLE_KILLME = True
CMD_HELP = {}
AFKREASON = None
ZALG_LIST = [[
    "̖",
    " ̗",
    " ̘",
    " ̙",
    " ̜",
    " ̝",
    " ̞",
    " ̟",
    " ̠",
    " ̤",
    " ̥",
    " ̦",
    " ̩",
    " ̪",
    " ̫",
    " ̬",
    " ̭",
    " ̮",
    " ̯",
    " ̰",
    " ̱",
    " ̲",
    " ̳",
    " ̹",
    " ̺",
    " ̻",
    " ̼",
    " ͅ",
    " ͇",
    " ͈",
    " ͉",
    " ͍",
    " ͎",
    " ͓",
    " ͔",
    " ͕",
    " ͖",
    " ͙",
    " ͚",
    " ",
],
             [
                 " ̍", " ̎", " ̄", " ̅", " ̿", " ̑", " ̆", " ̐", " ͒", " ͗",
                 " ͑", " ̇", " ̈", " ̊", " ͂", " ̓", " ̈́", " ͊", " ͋", " ͌",
                 " ̃", " ̂", " ̌", " ͐", " ́", " ̋", " ̏", " ̽", " ̉", " ͣ",
                 " ͤ", " ͥ", " ͦ", " ͧ", " ͨ", " ͩ", " ͪ", " ͫ", " ͬ", " ͭ",
                 " ͮ", " ͯ", " ̾", " ͛", " ͆", " ̚"
             ],
             [
                 " ̕",
                 " ̛",
                 " ̀",
                 " ́",
                 " ͘",
                 " ̡",
                 " ̢",
                 " ̧",
                 " ̨",
                 " ̴",
                 " ̵",
                 " ̶",
                 " ͜",
                 " ͝",
                 " ͞",
                 " ͟",
                 " ͠",
                 " ͢",
                 " ̸",
                 " ̷",
                 " ͡",
             ]]
