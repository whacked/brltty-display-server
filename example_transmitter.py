import sys
import requests
import json
from pprint import pprint
import receiver as SERVER

JSONRPC_VERSION = '2.0'

def main():
    url = 'http://{}:{}/jsonrpc'.format(SERVER.HOSTNAME, SERVER.PORT)
    headers = {'content-type': 'application/json'}
    payload = {
        'method': 'show',
        'params': [len(sys.argv) > 1 and sys.argv[-1] or 'hello world'],
        'jsonrpc': JSONRPC_VERSION,
        'id': 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()
    pprint(response)

if __name__ == '__main__':
    main()
