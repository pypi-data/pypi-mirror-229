"""Send a notification to a Telegram user or group.

E.g., send a notification triggered by some event in a monitoring system.
"""


__author__ = 'p4irin'
__email__ = '139928764+p4irin@users.noreply.github.com'
__version__ = '1.0.0'


import requests


class Notifier(object):
    """
    Sends notifications.

    Args:
        token: Telegram bot token
    """
    def __init__(self, token: str) -> None:
        self._base_url = f'https://api.telegram.org/bot{token}/'

    def _handle_requests_exceptions(method):
        """Decorate a method with exception handling for requests methods.
        
        Args:
            method: A method that uses a method of the requests module.

        Returns:
            Returns the method decorated with exception handling.
        """
        def decorated_f(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)            

        return decorated_f    

    @_handle_requests_exceptions
    def send(self, notification: str, to_chat_id: str) -> requests.Response:
        """Send a text notification.
        
        Args:
            notification: Tell the recipient(s) what happened.
            to_chat_id: Identifies a Telegram user or group.

        Returns:
            requests.Response: Allow the caller access to and handling the
                response

        Raises:
            SystemExit: On all exceptions
        """
        data = {
            'chat_id': to_chat_id,
            'text': notification
        }

        r = requests.get(
            f'{self._base_url}sendMessage',
            data=data
        )
        r.raise_for_status()
        return r
    
    @_handle_requests_exceptions
    def send_photo(
            self, photo: str, to_chat_id: str, caption: str="", 
        ) -> requests.Response:
        """Send a photo notification.
        
        Args:
            photo: The path to the photo.
            to_chat_id: Identifies a Telegram user or group.
            caption: Set a caption for the photo.

        Returns:
            requests.Response: Allow the caller access to and handling the
                response

        Raises:
            SystemExit: On all exceptions
        """
        data = {
            'chat_id': to_chat_id,
            'caption': caption
        }

        with open(photo, "rb") as photo:
            r = requests.post(
                f'{self._base_url}sendPhoto',
                data=data,
                files={'photo': photo}
            )
            r.raise_for_status()
            return r    
