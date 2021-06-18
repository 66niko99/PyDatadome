# PyDatadome

PyDatadome is a library to help you solve ReCaptcha based datadome. This library currently does not work with sites using funcaptcha/geetest, only ReCaptcha.

## Installation

Use [pip](https://pip.pypa.io/en/stable/) to install directly from github.

```bash
pip install git+https://github.com/66niko99/PyDatadome.git
```
## Usage


## *`class`* DatadomeHandler

#### *`arg`* captchaTokenFunction 
Pass a function that that returns a ReCaptcha token. You have to create this yourself. It should be be wrapped with lambda or without braces.

#### *`arg`* userAgent
The UserAgent your request client is using.

### *`method`* handleRequest(self, request, datadomeCookie)
#### *`arg`* request - the HTTP request you need to solve Datadome for
#### *`arg`* datadomeCookie- the client's datadome cookie

This is probably the only method you will need from this library. It converts a request response into a `/check` URL. Make a `/GET` request to this  URL and it will return a datadome cookie if everything worked. 

Here is an example of successful usage:
```python
ddHandler = DatadomeHandler(captchaTokenFunction=getCaptchaToken, userAgent=user_agent)
req = requests.get('https://www.example.com')

checkURL = ddHandler.handleRequest(request=req, datadomeCookie=req.cookies.get('datadome'))
checkDD = requests.get(checkURL)
print(checkDD.text) # {"cookie":"datadome=CBhqno..."}

```
**other methods are probably useless to you and are self explanitory. i dont want to write anymore docs.*

### *`Function`* PyDatadome.isRequestDatadome(request)
#### *`arg`* request 
Needs to be an http request (requests.post, requests.get, etc). It will return True if the request 
is a Datadome response, False otherwise

## Example script
[example.py](https://github.com/66niko99/PyDatadome/blob/master/example.py)
```python
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
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
