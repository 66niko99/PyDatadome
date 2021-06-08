import requests
from PyDatadome import DatadomeHandler, isRequestDatadome


# replace this function with your own recaptcha token function
def getCaptchaToken():
    return 'recaptcha token'

# creating request session
s = requests.session()
user_agent = 'Mozilla/5.0'
s.headers.update({'User-Agent': user_agent})

# creating datadome handler object, you must have a function that returns recaptcha tokens
ddHandler = DatadomeHandler(captchaTokenFunction=getCaptchaToken, userAgent=user_agent)

# make an http request to a datadome protected site
req = s.post('https://www.example.com', data={'username': 'joe', 'password': 'bob'})

# checking if the request response is a datadome block
if isRequestDatadome(req):
    # shiver me timbers! datadome! simply pass the request and datadome cookie to your datadome handler, and it
    # returns a valid /check endpoint.

    datadomeEndpoint = ddHandler.handleRequest(request=req, datadomeCookie=s.cookies.get('datadome'))

    url = ddHandler.buildUrlFromDict(ddHandler.buildDictFromResponse(req.text),
                                     datadomeCookie=s.cookies.get('datadome'), request=req)

    # make a GET request to the endpoint and the response will be a new datadome cookie!
    # note that if your recaptcha response was invalid, this will give you a 403/404 error or a blank page
    checkDatadome = s.get(datadomeEndpoint)

    # checking if endpoint was valid
    if checkDatadome.status_code == 200:
        # parse the response for a new cookie, then update your request clients cookies
        newCookie = checkDatadome.json()['cookie'].split(';')[0].replace('datadome=', '')
        s.cookies.set(name='datadome', value=newCookie)
    else:
        print('Error solving datadome')

# continue making requests in peace
