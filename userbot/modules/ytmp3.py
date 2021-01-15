import os

from pytube import YouTube
from pytube.helpers import safe_filename
from telethon import types
from userbot import CMD_HELP
from userbot.events import register
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2
from os import environ
from PIL import Image
msg_for_percantage = types.Message
@register(outgoing=True, pattern=r"^\.ytmp3 (\S*)")
async def youtube_mp3(ytmp3):
    if environ.get("isSuspended") == "True":
        return
    global msg_for_percentage
    reply_message = await ytmp3.get_reply_message()
    url = ytmp3.pattern_match.group(1)

    await ytmp3.edit("**Processing...**")

    video = YouTube(url)
    stream = video.streams.filter(only_audio=True, mime_type="audio/webm").last()
    os.system(f"wget -q -O 'picture.jpg' {video.thumbnail_url}")
    await ytmp3.edit("**Downloading audio...**")
    stream.download(filename=f'{safe_filename(video.title)}')
    await ytmp3.edit("**Converting to mp3...**")
    os.system(f"ffmpeg -loglevel panic -i '{safe_filename(video.title)}.webm' -vn -ab 128k -ar 44100 -y 'song.mp3'")
    #os.system(f"ffmpeg -i '{safe_filename(video.title)}.webm' -vn -ab 128k -ar 44100 -y '{safe_filename(video.title)}.mp3'")
#    try:
#        im = Image.open("picture.jpg")
#        width, height = im.size   # Get dimensions
#        left = (width - 500)/2
#        top = (height - 500)/2
#        right = (width + 500)/2
#        bottom = (height + 500)/2

        # Crop the center of the image
#        im = im.crop((left, top, right, bottom))
        #save resized image
#        im.save('picture.jpg')
        
#    except:
#        await ytmp3.edit("**Sending mp3...**")
#        await ytmp3.client.send_file(ytmp3.chat.id,
#                              f'song.mp3',
#                              caption=f"{video.title}",
#                              reply_to=reply_message, progress_callback=callback)
#        return
    audio = MP3(f"song.mp3", ID3=ID3)
    try:
        audio.add_tags()
    except error:
        pass
    await ytmp3.edit("**Adding tags...**")
    audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open('picture.jpg','rb').read()))
    audio.tags.add(TIT2(text=video.title))
    audio.save()
    await ytmp3.edit("**Sending mp3...**")
    msg_for_percentage = ytmp3
    await ytmp3.client.send_file(ytmp3.chat.id,
                              f'song.mp3',
                              caption=f"{video.title}",
                              reply_to=reply_message, progress_callback=callback)

    await ytmp3.delete()
    os.remove(f'song.mp3')
    os.remove('picture.jpg')
    
async def callback(current, total):
    global msg_for_percentage
    percent = round(current/total * 100, 2)
    await msg_for_percentage.edit(f"**Sending...**\nUploaded `{current}` out of `{total}` bytes: `{percent}%`")

CMD_HELP.update({"ytmp3": ["YtMP3",
    " - `.ytmp3 (url)`: Convert a YouTube video to a mp3 and send it.\n"
                        ]})
