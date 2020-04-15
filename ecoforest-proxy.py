"""
Ecoforest proxy to transform replies to JSON
"""

import sys, logging, datetime, urllib, urllib2, json, requests, urlparse, os
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler
from requests.auth import HTTPBasicAuth

# configuration
DEBUG = False
DEFAULT_PORT = 8998

username = os.environ['ECOFOREST_USERNAME']
passwd = os.environ['ECOFOREST_PASSWORD']
host = os.environ['ECOFOREST_HOST']

print()

ECOFOREST_URL = host + '/recepcion_datos_4.cgi'

if DEBUG:
    FORMAT = '%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')
else:
    FORMAT = '%(asctime)-0s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')


class EcoforestServer(BaseHTTPRequestHandler):

    def send(self, response):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response))
        except:
            self.send_error(500, 'Something went wrong here on the server side.')


    def healthcheck(self):
        self.send({'status': 'ok'})


    def stats(self):
        if DEBUG: logging.debug('GET stats')
        stats = self.ecoforest_stats()
        if stats:
            self.send(stats)
        else:
            self.send_error(500, 'Something went wrong here on the server side.')


    def set_status(self, status):
        if DEBUG: logging.debug('SET STATUS: %s' % (status))
        stats = self.ecoforest_stats()

        # only if 'estado' is off send request to turn on
        if status == "on" and stats['state'] == "off":
            data = self.ecoforest_call('idOperacion=1013&on_off=1')

        # only if 'estado' is on send request to turn off
        if status == "off" and (stats['state'] in ["on", "stand by", "starting"]):
            data = self.ecoforest_call('idOperacion=1013&on_off=0')

        self.send(self.get_status())


    def get_status(self):
        stats = self.ecoforest_stats()
        self.send(stats['state'])


    def set_temp(self, temp):
        if DEBUG: logging.debug('SET TEMP: %s' % (temp))
        if float(temp) < 12:
            temp = "12"
        if float(temp) > 40:
            temp = "30"
        # idOperacion=1019&temperatura
        data = self.ecoforest_call('idOperacion=1019&temperatura=' + temp)
        self.send(self.ecoforest_stats())


    def ecoforest_stats(self):
        stats = self.ecoforest_call('idOperacion=1002')
        reply = dict(e.split('=') for e in stats.text.split('\n')[:-1]) # discard last line ?

        states = {
            '0'  : 'off',
            '1'  : 'off',
            '2'  : 'starting',
            '3'  : 'starting',
            '4'  : 'starting',
            '5'  : 'starting',
            '10' : 'starting',
            '7'  : 'on',
            '8'  : 'shutting down',
            '-2' : 'shutting down',
            '9'  : 'shutting down',
            '11' : 'shutting down',
            '-3' : 'alarm',
            '-4' : 'alarm',
            '20' : 'stand by',
        }

        state = reply['estado']
        if state in states:
            reply['state'] = states[state]
        else:
            reply['state'] = 'unknown'
            logging.debug('reply: %s', reply)

        return reply


    # queries the ecoforest server with the supplied contents and parses the results into JSON
    def ecoforest_call(self, body):
        if DEBUG: logging.debug('Request:\n%s' % (body))
        headers = { 'Content-Type': 'application/json' }
        try:
            request = requests.post(ECOFOREST_URL, data=body, headers=headers, auth=HTTPBasicAuth(username, passwd), timeout=2.5)
            if DEBUG: logging.debug('Request:\n%s' %(request.url))
            if DEBUG: logging.debug('Result:\n%s' %(request.text))
            return request
        except requests.Timeout:
            pass


    def do_POST(self):
        parsed_path = urlparse.urlparse(self.path)
        args = dict()
        if parsed_path.query:
            args = dict(qc.split("=") for qc in parsed_path.query.split("&"))

        if DEBUG: logging.debug('GET: TARGET URL: %s, %s' % (parsed_path.path, parsed_path.query))
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)

        dispatch = {
            '/ecoforest/status': self.set_status,
        }

        # API calls
        if parsed_path.path in dispatch:
            try:
                dispatch[parsed_path.path](post_body, **args)
            except:
                self.send_error(500, 'Something went wrong here on the server side.')
        else:
            self.send_error(404,'File Not Found: %s' % parsed_path.path)

        return


    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        args = dict()
        if parsed_path.query:
            args = dict(qc.split("=") for qc in parsed_path.query.split("&"))

        dispatch = {
            '/healthcheck': self.healthcheck,
            '/ecoforest/fullstats': self.stats,
            '/ecoforest/status': self.get_status,
            '/ecoforest/set_status': self.set_status,
            '/ecoforest/set_temp': self.set_temp,
        }

        # API calls
        if parsed_path.path in dispatch:
            try:
                dispatch[parsed_path.path](**args)
            except:
                self.send_error(500, 'Something went wrong here on the server side.')
        else:
            self.send_error(404,'File Not Found: %s' % parsed_path.path)

        return


if __name__ == '__main__':
    try:
        from BaseHTTPServer import HTTPServer
        server = HTTPServer(('', DEFAULT_PORT), EcoforestServer)
        logging.info('Ecoforest proxy server started, with config host (%s) and username (%s)', host, username)
        logging.info('use {Ctrl+C} to shut-down ...')
        server.serve_forever()
    except Exception, e:
        logging.error(e)
        sys.exit(2)
