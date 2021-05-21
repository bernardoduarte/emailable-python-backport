import requests
from .response import Response
from .error import (ClientError, AuthError, PaymentRequiredError,
                    ResourceNotFoundError, RateLimitExceededError,
                    ServerUnavailableError)

class Client(object):

  def __init__(self, api_key):
    self.api_key = api_key
    self.base_url = 'https://api.emailable.com/v1/'

  def verify(self, email, smtp=True, accept_all=False, timeout=None):
    params = {
      'api_key': self.api_key,
      'email': email,
      'smtp': str(smtp).lower(),
      'accept_all': str(accept_all).lower(),
      'timeout': timeout
    }

    url = self.base_url + 'verify'
    return self.__request('get', url, params)

  def batch(self, emails, callback_url = None):
    if isinstance(emails, list):
      emails = ','.join(emails)

    params = {
        'api_key': self.api_key,
        'emails': emails,
        'url': callback_url
    }
    url = self.base_url + 'batch'
    return self.__request('post', url, params)

  def batch_status(self, batch_id):
    params = {
        'api_key': self.api_key,
        'id': batch_id
    }

    url = self.base_url + 'batch'
    return self.__request('get', url, params)

  def account(self):
    params = {
        'api_key': self.api_key
    }

    url = self.base_url + 'account'
    return self.__request('get', url, params)

  def __request(self, method, url, params):
    options = { 'params': params }

    try:
      response = requests.request(method, url, **options)
      response.raise_for_status()
      return Response(response)
    except requests.exceptions.RequestException as e:
      self.__handle_error(e, response)

  def __handle_error(self, e, response):
    status_code = response.status_code
    message = response.json()['message']
    if status_code == 401 or status_code == 403:
      raise AuthError(message)
    elif status_code == 402:
      raise PaymentRequiredError(message)
    elif status_code == 404:
      raise ResourceNotFoundError(message)
    elif status_code == 429:
      raise RateLimitExceededError(message)
    elif status_code == 503:
      raise ServerUnavailableError(message)
    else:
      raise ClientError(status_code, message)
