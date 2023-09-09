# telegram_notifier_bot - v1.0.0

A simple package to send notifications to a Telegram user or group. 

E.g.

- Send notifications triggered by some event
  - in a monitoring system
  - an IoT device
  - a service

## Installation

### From PyPI

```bash
(venv) $ pip install telegram-notifier-bot
(venv) $
```

### From GitHub

```bash
(venv) $ pip install git+https://github.com/p4irin/telegram_notifier_bot.git
(venv) $
```

### Verify

```bash
(venv) $ python
Python 3.8.10 (default, Jun  2 2021, 10:49:15) 
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import telegram_notifier_bot
>>> telegram_notifier_bot.__version__
'0.0.1'
>>>
```

## Usage

### Prerequisite

[Create a new Telegram bot](https://core.telegram.org/bots/features#creating-a-new-bot)

### Send a notification

```bash
(venv) $ export TELEGRAM_BOT_TOKEN=<Your Telegram bot token>
(venv) $ export TELEGRAM_CHAT_ID=<Recipient(s) chat or group id>
(venv) $ export TELEGRAM_PATH_TO_PHOTO=<File system path to photo>
(venv) $ python
Python 3.8.10 (default, Jun  2 2021, 10:49:15) 
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> from telegram_notifier_bot import Notifier
>>> token = os.getenv('TELEGRAM_BOT_TOKEN')
>>> chat_id = os.getenv('TELEGRAM_CHAT_ID')
>>> photo = os.getenv('TELEGRAM_PATH_TO_PHOTO')
>>> notifier = Notifier(token)
>>> notifier.send("We're out of coffee! Please fix ASAP!", chat_id)
>>> notifier.send_photo(photo, chat_id)
>>>
```

## Reference

- [The Telegram Bot API](https://core.telegram.org/bots/api)
- [Requests: HTTP for Humans](https://requests.readthedocs.io/en/latest/)