import argparse
import json
import pprint
import sys
import urllib
import urllib2

import oauth2

API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = "HdzlPZb_2xw6fqA2AzDYWA"
CONSUMER_SECRET = "FJWv60cVE1qB4PqrCbinx-Ta8_s"
TOKEN = "QA9fzFuwv5q_75mgGgDb6gJTsGoQxBxS"
TOKEN_SECRET = "dpM9Ruq7Ip6sXppnSTYy9UDC1IE"