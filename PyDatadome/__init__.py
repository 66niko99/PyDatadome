"""
Python library to help you solve ReCaptcha based datadome. This library currently does not work with
sites using funcaptcha, only ReCaptcha.

The main purpose of this package is to convert a request response into a /check url
that you can make a GET request to and receive a new datadome cookie.

This is how I approached handling datadome. If you have any bugs or suggestions please contact
me on discord @slim#8049 or make a pull request.
"""

from urllib.parse import urlparse, parse_qs
import json


def isRequestDatadome(request):
    """
    :param request: The request you want check for a datadome resposne
    :return: True if request is Datadome, otherwise false
    """

    if 'geo.captcha-delivery.com' in request.text.lower():
        return True

    return False


class DatadomeHandler:
    def __init__(self, captchaTokenFunction, userAgent):
        """
        :param captchaTokenFunction: Your function used to retrieve ReCaptcha tokens
        :param userAgent: The UA that your request client uses
        """

        self.userAgent = userAgent
        self.tokenFunction = captchaTokenFunction

    def handleRequest(self, request, datadomeCookie):
        """
        :param request: The HTTP request that was flagged by Datadome
        :param datadomeCookie: The datadome cookie used in the request
        """

        # MAKING SURE THE REQUEST IS A DATADOME RESPONSE
        if 'cid' not in request.text.lower():
            return KeyError('The request is not a Datadome response')

        # CHECKING IF DATADOME IS RECIEVED AS JSON URL: {"url": "..."}
        try:
            dd_url = request.json()['url']
        # CHECKING IF DATADOME IS RECEIVED AS DICTIONARY WITH DATA
        except (json.JSONDecodeError, KeyError):
            dd_text = request.text.split('var dd=')[1].split('</script>')[0].replace("'", '"')
            dd_url = self.buildUrlFromDict(json.loads(dd_text), datadomeCookie, request)

        if 't=bv' in dd_url:
            return ValueError('Datadome hard ban, t=bv found in URL')

        return self.buildCheckEndpoint(dd_url)

    def buildCheckEndpoint(self, captchaUrl):
        """
        :param captchaUrl: Builds /check endpoint from /captcha url
        :return: /check endpoint
        """

        parsed = urlparse(captchaUrl)
        urlQueries = parse_qs(parsed.query)

        # GETTING A RECAPTCHA TOKEN THE FUNCTION YOU PASSED
        token = self.tokenFunction()

        # BUILDING THE URL
        url = "https://geo.captcha-delivery.com/captcha/check"
        url += f"?cid={urlQueries['cid'][0]}"
        url += f"&icid={urlQueries['initialCid'][0]}"
        url += "&ccid=null"
        url += f"&g-recaptcha-response={token}"
        url += f"&hash={urlQueries['hash'][0]}"
        url += f"&ua={self.userAgent}"
        url += f"&referer={urlQueries['referer'][0]}"
        url += f"&parent_url={url}"
        url += f"&x-forwarded-for="
        url += "&captchaChallenge=15577870"
        url += f"&s={urlQueries['s'][0]}"

        return url

    @staticmethod
    def buildUrlFromDict(datadome_info: dict, datadomeCookie, request):
        """
        Builds /captcha url from Datadome dictionary
        :param datadome_info: Dictionary containing datadome information
        :param datadomeCookie: The datadome cookie used in the request
        :param request: The HTTP request that was flagged by Datadome
        :return: datadome captcha url
        """

        # BUILDING THE URL
        url = 'https://geo.captcha-delivery.com/captcha/'
        url += f'?initialCid={datadome_info["cid"]}'
        url += f'&cid={datadomeCookie}'
        url += f'&referer={request.url}'
        url += f'&hash={datadome_info["hsh"]}'
        url += f'&t={datadome_info["t"]}'
        url += f'&s={datadome_info["s"]}'
        url += f'&referer={request.url}'
        return url

    @staticmethod
    def buildDictFromResponse(requestResponse):
        return json.loads(requestResponse.split('var dd=')[1].split('</script>')[0].replace("'", '"'))
