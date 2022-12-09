# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing various scrapers. """

from os import environ
import os
from html import unescape
import re
from shutil import rmtree
from telethon import types, utils
from urllib.error import HTTPError
#from subprocess import call
from emoji import emoji_list
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import LANGUAGES, Translator
from pytube import YouTube
from pytube.helpers import safe_filename
from requests import get
from search_engine_parser import GoogleSearch
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError
from random_words import RandomWords
from userbot.utils import get_args_split_by
from userbot import (BOTLOG, BOTLOG_CHATID, CMD_HELP, CURRENCY_API,
                     YOUTUBE_API_KEY, bot, WOLFRAM_ID, BG_DEFAULT)
from userbot.events import register
from gtts import gTTS, gTTSError #tts
from bs4 import BeautifulSoup #imdb
import asyncurban #ud
from userbot.modules import speech


LANG = "en"
environ["enabled"] = "True"
environ["song"] = "r"

@register(outgoing=True, pattern="^.img (.*)")
async def img_sampler(event):
    """ For .img command, search and return images matching the query. """
    if environ.get("isSuspended") == "True":
        return
    await event.edit("Processing...")
    args = get_args_split_by(event.pattern_match.group(), ",")
    query_temp = args[0]
    query = query_temp.replace(" ","%20") #change every space symbol to %20 for browser search
    try:
        lim = args[1]
        lim = lim.replace("lim=", "")
        query = query.replace("lim=" + lim[0], "")
    except IndexError:
        lim = str(2)
    if os.path.isdir("downloads") is False:
      os.mkdir("downloads")
    os.system("chmod 0755 bing.py")
    os.system("./bing.py -nn -l " + lim + " -u https://www.bing.com/images/search?q=" + query)
    #TODO: make a sending as album
    for filename in os.listdir("downloads"):
      #paths = 'downloads/' + filename + ', '
      await event.client.send_file(event.chat.id, file='downloads/' + filename)
    rmtree("downloads")
    await event.delete()

@register(outgoing=True, pattern="^.ranimg")
async def img_sam(event):
    """ For .img command, search and return images matching the query. """
    if environ.get("isSuspended") == "True":
        return
    await event.edit("Processing...")
    query = RandomWords().random_word()
    await event.edit("**Random word is: **" + query)
    if os.path.isdir("downloads") is False:
      os.mkdir("downloads")
    os.system("./bing.py -nn -l " + "2" + " -u https://www.bing.com/images/search?q=" + query)
    #TODO: make a sending as album
    for filename in os.listdir("downloads"):
      #paths = 'downloads/' + filename + ', '
      await event.client.send_file(event.chat.id, file='downloads/' + filename)
    rmtree("downloads")
    
@register(outgoing=True, pattern=r"^.wiki (.*)")
async def wiki(wiki_q):
    """ For .google command, fetch content from Wikipedia. """
    if environ.get("isSuspended") == "True":
        return
    match = wiki_q.pattern_match.group(1)
    try:
        summary(match)
    except DisambiguationError as error:
        await wiki_q.edit(f"Disambiguated page found.\n\n{error}")
        return
    except PageError as pageerror:
        await wiki_q.edit(f"Page not found.\n\n{pageerror}")
        return
    result = summary(match)
    if len(result) >= 4096:
        file = open("output.txt", "w+")
        file.write(result)
        file.close()
        await wiki_q.client.send_file(
            wiki_q.chat_id,
            "output.txt",
            reply_to=wiki_q.id,
            caption="`Output too large, sending as file`",
        )
        if os.path.exists("output.txt"):
            os.remove("output.txt")
        return
    await wiki_q.edit("**Search:**\n`" + match + "`\n\n**Result:**\n" + result)
    if BOTLOG:
        await wiki_q.client.send_message(
            BOTLOG_CHATID, f"Wiki query {match} was executed successfully")


@register(outgoing=True, pattern="^\.ud (.*)")
async def urban_dict(ud_e):
    """ For .ud command, fetch content from Urban Dictionary. """
    if environ.get("isSuspended") == "True":
        return
    await ud_e.edit("Processing...")
    query = ud_e.pattern_match.group(1)
    urban_dict_helper = asyncurban.UrbanDictionary()
    try:
        urban_def = await urban_dict_helper.get_word(query)
    except asyncurban.WordNotFoundError:
        await ud_e.edit(f"Sorry, couldn't find any results for: {query}")
        return
    deflen = sum(len(i) for i in urban_def.definition)
    exalen = sum(len(i) for i in urban_def.example)
    meanlen = deflen + exalen
    if int(meanlen) >= 0:
        if int(meanlen) >= 4096:
            await ud_e.edit("`Output too large, sending as file.`")
            file = open("output.txt", "w+")
            file.write("Text: " + query + "\n\nMeaning: " +
                       urban_def.definition + "\n\n" + "Example: \n" +
                       urban_def.example)
            file.close()
            await ud_e.client.send_file(
                ud_e.chat_id,
                "output.txt",
                caption="`Output was too large, sent it as a file.`")
            if os.path.exists("output.txt"):
                os.remove("output.txt")
            await ud_e.delete()
            return
        await ud_e.edit("Text: **" + query + "**\n\nMeaning: **" +
                        urban_def.definition + "**\n\n" + "Example: \n__" +
                        urban_def.example + "__")
        if BOTLOG:
            await ud_e.client.send_message(
                BOTLOG_CHATID, "UrbanDictionary query for `" + query +
                "` executed successfully.")
    else:
        await ud_e.edit("No result found for **" + query + "**")


@register(outgoing=True, pattern=r"^.tts(?: |$)([\s\S]*)")
async def text_to_speech(query):
    """ For .tts command, a wrapper for Google Text-to-Speech. """
    if environ.get("isSuspended") == "True":
        return
    textx = await query.get_reply_message()
    message = query.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await query.edit("`Give a text or reply to a "
                         "message for Text-to-Speech!`")
        return

    try:
        tts = gTTS(message, tld='com', lang=LANG)
        tts.save("k.mp3")
    except AssertionError:
        await query.edit('The text is empty.\n'
                         'Nothing left to speak after pre-precessing, '
                         'tokenizing and cleaning.')
        return
    except ValueError:
        await query.edit('Language is not supported.')
        return
    except RuntimeError:
        await query.edit('Error loading the languages dictionary.')
        return
    except gTTSError:
        await query.edit('Error in Google Text-to-Speech API request! '
                         'Check Paperplane logs for details.')
        return

    with open("k.mp3", "r"):
        await query.client.send_file(query.chat_id, "k.mp3", voice_note=True)
        os.remove("k.mp3")
        if BOTLOG:
            await query.client.send_message(
                BOTLOG_CHATID, "TTS of " + message + " executed successfully!")
        await query.delete()

@register(outgoing=True, pattern=r"^.trt(?: |$)([\s\S]*)")
async def translateme(trans):
    """ For .trt command, translate the given text using Google Translate. """
    if environ.get("isSuspended") == "True":
        return
    translator = Translator()
    textx = await trans.get_reply_message()
    message = trans.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await trans.edit("`Give a text or reply "
                         "to a message to translate!`")
        return

    try:
        reply_text = translator.translate(deEmojify(message), dest=LANG)
    except ValueError:
        await trans.edit("Invalid destination language.")
        return

    source_lan = LANGUAGES[f'{reply_text.src.lower()}']
    transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']
    reply_text = f"**Source ({source_lan.title()}):**`\n{message}`**\n\
\nTranslation ({transl_lan.title()}):**`\n{reply_text.text}`"

    await trans.client.send_message(trans.chat_id, reply_text)
    await trans.delete()
    if BOTLOG:
        await trans.client.send_message(
            BOTLOG_CHATID,
            f"Translate query {message} was executed successfully",
        )


@register(pattern="^.lang (.*)", outgoing=True)
async def lang(value):
    """ For .lang command, change the default langauge of userbot scrapers. """
    if environ.get("isSuspended") == "True":
        return
    global LANG
    LANG = value.pattern_match.group(1)
    await value.edit("Default language changed to **" + LANG + "**")
    if BOTLOG:
        await value.client.send_message(
            BOTLOG_CHATID, "Default language changed to **" + LANG + "**")

@register(outgoing=True, pattern=r"^.cr (.*)")
async def _(event):
    if environ.get("isSuspended") == "True":
        return
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@",
                                                             "!"):
        if event.fwd_from:
            return
        input_str = event.pattern_match.group(1)
        input_sgra = input_str.split(" ")
        if len(input_sgra) == 3:
            try:
                number = float(input_sgra[0])
                currency_from = input_sgra[1].upper()
                currency_to = input_sgra[2].upper()
                request_url = "https://api.exchangeratesapi.io/latest?base={}".format(
                    currency_from)
                current_response = get(request_url).json()
                if currency_to in current_response["rates"]:
                    current_rate = float(
                        current_response["rates"][currency_to])
                    rebmun = round(number * current_rate, 2)
                    await event.edit("{} {} = {} {}".format(
                        number, currency_from, rebmun, currency_to))
                else:
                    await event.edit(
                        "`This seems to be some alien currency, which I can't convert right now.`"
                    )
            except Exception as e:
                await event.edit(f"Error: {str(e)}")
        else:
            await event.edit("`Invalid syntax.`")
            return


def deEmojify(inputString):
    """ Remove emojis and other non-safe characters from string """
    return emoji_list().sub(u'', inputString)

@register(outgoing=True, pattern=r'^.wolfram (.*)')
async def wolfram(wvent):
    """ Wolfram Alpha API """
    if environ.get("isSuspended") == "True":
        return
    if WOLFRAM_ID is None:
        await wvent.edit(
            'Please set your WOLFRAM_ID first !\n'
            'Get your API KEY from [here](https://'
            'products.wolframalpha.com/api/)',
            parse_mode='Markdown')
        return
    i = wvent.pattern_match.group(1)
    appid = WOLFRAM_ID
    server = f'https://api.wolframalpha.com/v1/spoken?appid={appid}&i={i}'
    res = get(server)
    await wvent.edit(f'**{i}**\n\n' + res.text, parse_mode='Markdown')
    if BOTLOG:
        await wvent.client.send_message(
            BOTLOG_CHATID, f'.wolfram {i} was executed successfully')

        
#kanged from Paperplane Extended. Paperplane kang from from Blank-x. Lol
@register(outgoing=True, pattern="^.imdb (.*)")
async def imdb(e):
    if environ.get("isSuspended") == "True":
        return
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        try:
            movie_name = e.pattern_match.group(1)
            remove_space = movie_name.split(' ')
            final_name = '+'.join(remove_space)
            page = get("https://www.imdb.com/find?ref_=nv_sr_fn&q=" +
                       final_name + "&s=all")
            lnk = str(page.status_code)
            soup = BeautifulSoup(page.content, 'lxml')
            odds = soup.findAll("tr", "odd")
            mov_title = odds[0].findNext('td').findNext('td').text
            mov_link = "http://www.imdb.com/" + \
                odds[0].findNext('td').findNext('td').a['href']
            page1 = get(mov_link)
            soup = BeautifulSoup(page1.content, 'lxml')
            if soup.find('div', 'poster'):
                poster = soup.find('div', 'poster').img['src']
            else:
                poster = ''
            if soup.find('div', 'title_wrapper'):
                pg = soup.find('div', 'title_wrapper').findNext('div').text
                mov_details = re.sub(r'\s+', ' ', pg)
            else:
                mov_details = ''
            credits = soup.findAll('div', 'credit_summary_item')
            if len(credits) == 1:
                director = credits[0].a.text
                writer = 'Not available'
                stars = 'Not available'
            elif len(credits) > 2:
                director = credits[0].a.text
                writer = credits[1].a.text
                actors = []
                for x in credits[2].findAll('a'):
                    actors.append(x.text)
                actors.pop()
                stars = actors[0] + ',' + actors[1] + ',' + actors[2]
            else:
                director = credits[0].a.text
                writer = 'Not available'
                actors = []
                for x in credits[1].findAll('a'):
                    actors.append(x.text)
                actors.pop()
                stars = actors[0] + ',' + actors[1] + ',' + actors[2]
            if soup.find('div', "inline canwrap"):
                story_line = soup.find('div',
                                       "inline canwrap").findAll('p')[0].text
            else:
                story_line = 'Not available'
            info = soup.findAll('div', "txt-block")
            if info:
                mov_country = []
                mov_language = []
                for node in info:
                    a = node.findAll('a')
                    for i in a:
                        if "country_of_origin" in i['href']:
                            mov_country.append(i.text)
                        elif "primary_language" in i['href']:
                            mov_language.append(i.text)
            if soup.findAll('div', "ratingValue"):
                for r in soup.findAll('div', "ratingValue"):
                    mov_rating = r.strong['title']
            else:
                mov_rating = 'Not available'
            await e.edit(
                '<a href=' + poster + '>&#8203;</a>'
                '<b>Title : </b><code>' + mov_title + '</code>\n<code>' +
                mov_details + '</code>\n<b>Rating : </b><code>' + mov_rating +
                '</code>\n<b>Country : </b><code>' + mov_country[0] +
                '</code>\n<b>Language : </b><code>' + mov_language[0] +
                '</code>\n<b>Director : </b><code>' + director +
                '</code>\n<b>Writer : </b><code>' + writer +
                '</code>\n<b>Stars : </b><code>' + stars +
                '</code>\n<b>IMDB Url : </b>' + mov_link +
                '\n<b>Story Line : </b>' + story_line,
                link_preview=True,
                parse_mode='HTML')
        except IndexError:
            await e.edit("Plox enter **Valid movie name** kthx")
            
#voice note
@register(outgoing=True, pattern="^.a (.*)")
async def voice_note(event):
    if environ.get("isSuspended") == "True":
        return
    try:
        chat = await event.get_chat()
        await event.delete()
        async with event.client.action(chat, 'record-voice'):
            origin_text = event.message.text.replace('.a ', '')
            voicename, _duration = speech.syntese(origin_text, background = True)

            chat = await event.get_chat()
            wafe_form = speech.get_waveform(0, 31, 100)
            await event.client.send_file(chat, voicename, reply_to = event.message.reply_to_msg_id, attributes=[types.DocumentAttributeAudio(duration=_duration, voice=True, waveform=utils.encode_waveform(bytes(wafe_form)))]) # 2**5 because 5-bit

            speech.try_delete(voicename)

    except Exception as e:
        print(e)

#video note
@register(outgoing=True, pattern="^.v (.*)")
async def video_note(event):
    if environ.get("isSuspended") == "True":
        return
    try:
        chat = await event.get_chat()
        await event.delete()
        async with event.client.action(chat, 'record-round'):
            # make sound
            origin_text = event.message.text.replace('.v ', '')
            voicename, _duration = speech.syntese(origin_text, gender=1)
            # voicename, _duration = speech.syntese(origin_text, frequency=0.6, gender=1)

            # mount to video
            video_file = speech.mount_video(voicename)

            chat = await event.get_chat()
            await event.client.send_file(chat, video_file, reply_to = event.message.reply_to_msg_id, video_note=True)

            speech.try_delete(voicename)
            speech.try_delete(video_file)

    except Exception as e:
        print(e)

#demon voice note
@register(outgoing=True, pattern="^.d (.*)")
async def demon_voice(event):
    if environ.get("isSuspended") == "True":
        return
    try:
        chat = await event.get_chat()
        await event.delete()
        async with event.client.action(chat, 'record-voice'):
            origin_text = event.message.text.replace('.d ', '')
            voicename, _duration = speech.demon(origin_text)

            chat = await event.get_chat()
            wafe_form = speech.get_waveform(0, 31, 100)
            await event.client.send_file(chat, voicename, reply_to = event.message.reply_to_msg_id, attributes=[types.DocumentAttributeAudio(duration=_duration, voice=True, waveform=utils.encode_waveform(bytes(wafe_form)))]) # 2**5 because 5-bit

            speech.try_delete(voicename)

    except Exception as e:
        print(e)

#background voice note
@register(outgoing=True, disable_edited=True, disable_errors=True)
async def voice(event):
    if environ.get("isSuspended") == "True" or environ.get("BG_DEFAULT") == 0 or environ.get("BG_DEFAULT") == '0' or environ.get("BG_DEFAULT") == None:
        return
    is_enabled = environ.get("enabled", "True")
    if is_enabled == "True":
      if event.forward:
        return
      if event.voice:
          chat = await event.get_chat()
          await event.delete()
          async with event.client.action(chat, 'record-voice'):
              path_to_voice = await event.download_media()
              voicename, _duration = speech.megre_sounds(path_to_voice, environ["BG_DEFAULT"])

              chat = await event.get_chat()
              wafe_form = speech.get_waveform(0, 31, 100)
              await event.client.send_file(chat, voicename, reply_to = event.message.reply_to_msg_id, attributes=[types.DocumentAttributeAudio(duration=_duration, voice=True, waveform=utils.encode_waveform(bytes(wafe_form)))]) # 2**5 because 5-bit

              speech.try_delete(voicename)
            
@register(outgoing=True, pattern="^.bgon")    
async def enable(bg):
  if environ.get("isSuspended") == "True":
        return
  environ["enabled"] = "True"
  await bg.edit("**Background sound for voice messages enabled!**")

@register(outgoing=True, pattern="^.bgoff")    
async def disable(bg):
  if environ.get("isSuspended") == "True":
        return
  environ["enabled"] = "False"
  await bg.edit("**Background sound for voice messages disabled!**")

@register(outgoing=True, pattern="^.bg (.*)")    
async def change(bg):
  if environ.get("isSuspended") == "True":
        return
  sound_name = str(bg.pattern_match.group(1).split(' ', 1)[0])
  name_ogg = sound_name + '.ogg'
  files = os.listdir('media/')
  if name_ogg in files:
    environ["BG_DEFAULT"] = sound_name
    await bg.edit(f"**Background sound has been set to** `{name_ogg}`")
  else:
    await bg.edit(f"**There's no this file: {name_ogg}**")
    return
  
@register(outgoing=True, pattern="^.bgs")    
async def all_files(bg):
  if environ.get("isSuspended") == "True":
        return
  
  files = os.listdir('media/')
  await bg.edit(f"**Files in folder /media:** `{files}`")
  
CMD_HELP.update({"scrapers": ['Scrapers',
    " - `.img <query> lim=<n>`: Do an Image Search on Bing and send n results. Default is 2.\n"
    " - `.ranimg`: Do an Random Image Search on Bing and send 2 results."
    " - `.google <query>`: Search Google for query (argument or reply).\n"
    " - `.wiki <query>`: Search Wikipedia for query.\n"
    " - `.ud <query>`: Search on Urban Dictionary for query.\n"
    " - `.tts <query>`: Text-to-Speech the query (argument or reply) to the saved language.\n"
    " - `.trt <query>`: Translate the query (argument or reply) to the saved language.\n"
    " - `.lang <lang>`: Changes the default language of trt and TTS modules.\n"
    " -  `.imdb <movie-name>`: Shows movie info and other stuffs\n"
    " -  `.bg <file-name without .ogg>`: Changes deafult background music to file name\n"
    " -  `.bgs`: List of all files in /media\n"

    " - `.wolfram <query>: Get answers to questions using WolframAlpha Spoken Results API."]
})
