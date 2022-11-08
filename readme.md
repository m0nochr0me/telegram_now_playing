# Now Playing for Telegram

Set your profile photo and user info to track currently playing in Clementine.

# Stack

* Telethon
* matplotlib
* Pillow
* DBUS

# Prepare

Register app at [https://my.telegram.org/apps](https://my.telegram.org/apps).

Optional: Install [Code2000 font](https://www.code2000.net/code2000_page.html)

# Config

Copy or rename `config.example.yaml` to `config.example`. Then edit latter:

* set `api_id` and `api_hash` of your app
* set your username
* adjust font 
* set default profile photo and account info that will be restored on exit

# Note

Upon running this script all your profile photos will be deleted without prompt. Consider backup.
