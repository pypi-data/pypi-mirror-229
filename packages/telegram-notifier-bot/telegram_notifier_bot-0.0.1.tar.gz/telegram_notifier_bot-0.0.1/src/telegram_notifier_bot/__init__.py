"""Send a notification to a Telegram user or group.

E.g., send a notification triggered by some event in a monitoring system.
"""


__author__ = 'p4irin'
__email__ = '139928764+p4irin@users.noreply.github.com'
__version__ = '0.0.1'


import requests


def send(token: str, chat_id: str, notification: str) -> requests.Response:
    """Send a notification.
    
    Args:
        token: The Telegram bot token
        chat_id: Identifies a Telegram user or group
        notification: Tell the recipient(s) what happened

    Returns:
        requests.Response: Allow the caller access to and handling the response

    Raises:
        SystemExit: On all exceptions
    """
    try:
        r = requests.get(
            f'https://api.telegram.org/bot{token}/sendMessage?'
            + f'chat_id={chat_id}&text={notification}'
        )
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
