# BRL connection logic modified from https://github.com/brltty/brltty/blob/aba3d8cc2dc765a0933aabb609928e568e085d39/Bindings/Python/apitest.py
# distributed under LGPL. see original file as linked above

import sys
import time
import logging
import brlapi
import errno
import atexit

from flask import Flask, request, Response
from jsonrpcserver import method, dispatch
from flask_cors import CORS


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

HOSTNAME = 'localhost'
PORT = 8111

_Display = None
# PACmate 40
DISPLAY_SIZE = 40


app = Flask(__name__)
CORS(app, supports_credentials=True)

@method
def show(text):
    if text.strip() == '':
        if _Display:
            display_size = _Display.displaySize[0]
        else:
            display_size = DISPLAY_SIZE
        text = ' ' * display_size
    if _Display:
        logger.debug('showing text: >>{}<<'.format(text))
        _Display.writeText(text)
    return len(text)


@app.route('/jsonrpc', methods=['POST'])
def jsonrpc():
    req = request.get_data().decode()
    response = dispatch(req)
    return Response(str(response),
                    response.http_status,
                    mimetype='application/json')


def initialize_display():
    def writeProperty(name, value):
        sys.stdout.write(f'{name:>20}:\t{value}\n')

    writeProperty('BrlAPI Version', '.'.join(
        map(str, brlapi.getLibraryVersion())))

    try:
        # to specify explicit key:
        # brl = brlapi.Connection(b'127.0.0.1:0', b'/etc/brlapi.key')
        brl = brlapi.Connection()
        try:
            disp_ncol, disp_nrow = brl.displaySize
            writeProperty('File Descriptor', brl.fileDescriptor)
            writeProperty('Server Host', brl.host.decode('utf-8'))
            writeProperty('Authorization', brl.auth.decode('utf-8'))
            writeProperty('Driver Name', brl.driverName.decode('utf-8'))
            writeProperty('Model Identifier',
                          brl.modelIdentifier.decode('utf-8'))
            writeProperty('Display Size', f'{disp_nrow} x {disp_ncol}')

            brl.enterTtyMode(brl.fileDescriptor)
            return brl
        except Exception as e:
            print('Exception on info display: {}'.format(e))
    except brlapi.ConnectionError as e:
        if e.brlerrno == brlapi.ERROR_CONNREFUSED:
            logger.error('Connection to %s refused. BRLTTY is too busy...' % e.host)
        elif e.brlerrno == brlapi.ERROR_AUTHENTICATION:
            logger.error('Authentication with %s failed. Please check the permissions of %s' % (e.host, e.auth))
        elif e.brlerrno == brlapi.ERROR_LIBCERR and (e.libcerrno == errno.ECONNREFUSED or e.libcerrno == errno.ENOENT):
            logger.error('Connection to %s failed. Is BRLTTY really running?' % (e.host))
        else:
            logger.error('Connection to BRLTTY at %s failed: ' % (e.host))
        print(e)
        print(e.brlerrno)
        print(e.libcerrno)


def terminate_display(brl):
    brl.leaveTtyMode()
    brl.closeConnection()
    

if __name__ == '__main__':
    if 'test' in sys.argv:
        _Display = initialize_display()
        _Display.writeText('pack my box with five dozen liquor jugs')
        time.sleep(3)
        terminate_display()

    if 'server' in sys.argv:
        logger.debug('initializing display...')
        _Display = initialize_display()
        logger.debug('starting server...')
        @atexit.register
        def cleanup():
            logger.debug('cleaning up...')
            terminate_display(_Display)
        app.run(host=HOSTNAME, port=PORT)
