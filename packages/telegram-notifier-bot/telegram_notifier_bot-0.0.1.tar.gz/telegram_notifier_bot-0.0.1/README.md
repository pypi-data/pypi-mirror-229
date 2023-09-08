# telegram_notifier_bot - v0.0.1

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
(venv) $ python
Python 3.8.10 (default, Jun  2 2021, 10:49:15) 
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> import telegram_notifier_bot
>>> token = os.getenv('TELEGRAM_BOT_TOKEN')
>>> chat_id = os.getenv('TELEGRAM_CHAT_ID')
>>> telegram_notifier_bot.send(token, chat_id, "We're out of coffee! Please fix ASAP!")
>>>
```

## Reference

- [The Telegram Bot API](https://core.telegram.org/bots/api)
- [Requests: HTTP for Humans](https://requests.readthedocs.io/en/latest/)