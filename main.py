"""
Set Telegram profile image and about text to now plaing track in Clementine

m0nochr0me ❌ 2022
"""

import sys
import time
import yaml
import random
import textwrap
import dbus
from dbus.exceptions import DBusException
from PIL import Image, ImageDraw, ImageFont, ImageColor
from matplotlib import font_manager
from telethon import TelegramClient
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest


# Config
with open('config.yaml', mode='r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Init Telegram client
client = TelegramClient(config['tg']['user'], config['tg']['app_id'], config['tg']['app_hash'])

# Init DBUS
bus = dbus.SessionBus()
while True:
    try:
        obj = bus.get_object('org.mpris.MediaPlayer2.clementine', '/org/mpris/MediaPlayer2')
        interface = dbus.Interface(obj, 'org.freedesktop.DBus.Properties')
        break
    except DBusException:
        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)

# Prepare font
font_properties = font_manager.FontProperties(family=config['font']['family'], weight=config['font']['weight'])
font_file = font_manager.findfont(font_properties)
font = ImageFont.truetype(font_file, config['font']['size'])

# Global metadata variable
metadata = dbus.Dictionary()


def rndcol(saturation=86, value=85) -> tuple:
    """Return random hue color"""
    return ImageColor.getrgb(f'hsv({random.randint(1,359)}, {saturation}%, {value}%)')


async def make_image(artist, track) -> None:
    """Save image with given artist and track"""
    size = config['img']['size']
    margin = config['img']['margin']
    img = Image.new('RGB', (size, size), color=rndcol(30, 13))
    d = ImageDraw.Draw(img)
    d.multiline_text((size//2, size//2-margin),
                     textwrap.fill(artist, config['img']['wrap']),
                     fill=rndcol(),
                     anchor='md',
                     font=font)
    d.multiline_text((size//2, size//2+margin),
                     textwrap.fill(track, config['img']['wrap']),
                     fill=rndcol(),
                     anchor='ma',
                     font=font)
    img.save('out.png', 'PNG')


async def get_metadata() -> tuple:
    """Get metadata from media player"""
    global metadata
    try:
        new_metadata = interface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
        status = interface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
    except DBusException as e:
        return False, '-', '-'

    if new_metadata != metadata:
        metadata = new_metadata
        if status != 'Playing':
            return True, config['default']['artist'], config['default']['track']
        artist = metadata.get('xesam:artist', ['--'])[0]
        track = metadata.get('xesam:title', '--')
        random.seed(artist + track)
        print(f'{artist} -- {track}')
        return True, artist, track
    return False, '-', '-'


async def upd_photo(photo='out.png') -> None:
    """Update profile photo"""
    await client(DeletePhotosRequest(await client.get_profile_photos('me')))
    await client(UploadProfilePhotoRequest(await client.upload_file(photo)))


async def upd_info(bio) -> None:
    """Update profile info"""
    await client(UpdateProfileRequest(about=bio))


async def restore() -> None:
    """Restore profile photo and info"""
    await upd_info(config['default']['bio'])
    await upd_photo(config['default']['photo'])


async def main() -> None:
    try:
        while True:
            _r, artist, track = await get_metadata()
            if _r:
                await make_image(artist, track)
                await upd_photo()
                await upd_info(f'🎵: {artist} - {track}')
            time.sleep(1)
    except KeyboardInterrupt:
        await restore()
        sys.exit(0)


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
